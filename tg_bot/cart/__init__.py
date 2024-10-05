import asyncio
import base64
from datetime import date, datetime, timedelta
from typing import Callable, Coroutine

from geopy.geocoders import Nominatim

from django.utils import timezone
from redis import Redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, LabeledPrice, Message
from telegram.ext import MessageHandler
from telegram.ext import filters, CallbackQueryHandler,CommandHandler

from bot.models import User
from data.filial.models import Filial
from data.promocode.models import Promocode
from tg_bot.cart.back import CartBack
from tg_bot.constants import (
    CART,
    CART_COMMENT,
    CART_CONFIRM,
    CART_DELIVER_LOCATION_CONFIRM,
    CART_GET_METHOD,
    CART_PAYMENT,
    CART_PROMOCODE,
    CART_PHONE_NUMBER,
    CART_TAKEAWAY_FILIAL,
    CART_TIME,
    CART_TIME_LATER_TIME,
    CASH,
    CLICK,
    CTX,
    DELIVERY_LOCATION,
    EXCLUDE,
    LANG,
    MAIN_MENU,
    MENU,
    MENU_CATEGORY,
    MENU_PRODUCT,
    PAYME,
    PAYMENT_METHOD,
    PRODUCT_INFO,
    UPD,
)
from tg_bot.redis_conversation import ConversationHandler
from utils import ReplyKeyboardMarkup, distribute, get_later_times
from utils.language import multilanguage
from tg_bot.common_file import CommonKeysMixin


class TgBotCart(CartBack, CommonKeysMixin):
    redis: Redis
    CLICK_TOKEN: str
    PAYME_TOKEN: str

    def _cart_handlers(self, back_handler: Callable[[UPD, CTX], Coroutine] | None = None):

        
        
        return ConversationHandler(
            "CartConversation",
            [
                MessageHandler(
                    filters.Text(multilanguage.get_all("menu.cart")), self.cart
                )
            ],
            {

                CART: [
                    MessageHandler(
                        filters.Text(multilanguage.get_all("cart.done")), self.cart_done
                    ),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("buttons.clear")),
                        self.cart_clear,
                    ),
                    CallbackQueryHandler(self.cart_set_count, pattern=r"set_count"),
                    CallbackQueryHandler(self.cart_remove_item, pattern=r"remove"),
                    self.back(self.back_from_cart(back_handler)),
                ],
                
                
                
                
                CART_GET_METHOD: [
                    MessageHandler(
                        filters.Text(multilanguage.get_all("cart.deliver")),
                        self.cart_get_method_deliver,
                    ),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("cart.take_away")),
                        self.cart_get_method_take_away,
                    ),
                    self.back(self.cart),
                ],
                DELIVERY_LOCATION: [
                    MessageHandler(filters.LOCATION, self.cart_delivery_location),
                    self.back(self.back_from_cart_delivery_location),
                ],
                CART_DELIVER_LOCATION_CONFIRM: [
                    MessageHandler(filters.LOCATION, self.cart_delivery_location),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("buttons.confirm")),
                        self.cart_deliver_location_confirm,
                    ),
                    self.back(self.back_from_cart_delivery_location_confirm),
                ],
                CART_TAKEAWAY_FILIAL: [
                    MessageHandler(
                        filters.LOCATION, self.cart_takeaway_filial_location
                    ),
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_takeaway_filial),
                    self.back(self.back_from_cart_takeaway_filial),
                ],
                
                
                
                
                
                

                CART_TIME: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_time),
                    self.back(self.back_from_cart_time),
                ],
                CART_TIME_LATER_TIME: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_time_later_time),
                    self.back(self.back_from_cart_time_later_time),
                ],

                CART_PHONE_NUMBER: [
                    MessageHandler(
                        filters.CONTACT | (filters.TEXT & EXCLUDE),
                        self.cart_phone_number,
                    ),
                    self.back(self.back_from_cart_phone_number),
                ],
                CART_COMMENT: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_comment),
                    self.back(self.back_from_cart_comment),
                ],
                CART_PROMOCODE: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_promocode),
                    self.back(self.back_from_cart_coupon),
                ],
                CART_CONFIRM: [
                    MessageHandler(
                        filters.Text(multilanguage.get_all("buttons.confirm")),
                        self.cart_confirm,
                    ),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("buttons.cancel")),
                        self.cart_reject,
                    ),
                    self.back(
                        self.back_from_cart_confirm
                    )
                ],
                PAYMENT_METHOD: [
                    MessageHandler(filters.Text(multilanguage.get_all("payment.click","payment.payme","payment.cash")) & EXCLUDE, self.cart_payment_method)
                ],
                CART_PAYMENT: [
                    CallbackQueryHandler(self.back_from_cart_payment, pattern="back")
                ]
            },
            [
                CommandHandler('start',self.start)
            ],
            self.redis,
            True,
            {
                MENU: MENU,
                MAIN_MENU: MAIN_MENU,
                MENU_CATEGORY: MENU_CATEGORY,
                MENU_PRODUCT: MENU_PRODUCT,
                PRODUCT_INFO: PRODUCT_INFO,
                LANG: LANG,
            },
        )

    async def cart_keyboard(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        items = user.cart.items.all()

        keyboard = []

        for i, item in enumerate(items, 1):

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{i}. {i18n.get_name(item.product)} ❌",
                        callback_data=f"remove:{item.id}",
                    )
                ]
            )

            row = []

            if item.count > 0:
                row.append(
                    InlineKeyboardButton(
                        "➖", callback_data=f"set_count:reduce:{item.id}"
                    )
                )

            row.append(
                InlineKeyboardButton(f"{item.count}", callback_data=f"info:{item.id}")
            )

            row.append(
                InlineKeyboardButton(
                    f"➕", callback_data=f"set_count:increase:{item.id}"
                )
            )
            keyboard.append(row)

        return InlineKeyboardMarkup(keyboard)

    async def cart(self, update: UPD, context: CTX, edit: bool = False):
        tg_user, user, temp, i18n = User.get(update)

        if not edit:
            instruction = await tg_user.send_message(
                i18n.cart.instruction(),
                reply_markup=ReplyKeyboardMarkup(
                    [[i18n.buttons.back(), i18n.buttons.clear()], [i18n.cart.done()]],
                    False,
                ),
                parse_mode="HTML",
            )

            temp.message_id2 = instruction.message_id
            temp.save()

        items = user.cart.items.all()

        if items.count() == 0:
            await tg_user.send_message(i18n.cart.empty(), parse_mode="HTML")
            await self.delete_messages(update, context)
            return await self.start(update, context)

        items_text = []
        total_price = 0

        for i, item in enumerate(items, 1):
            product_name = (
                i18n.get_name(item.product) if item.product else "Unnamed product"
            )

            item_price = item.price * item.count
            total_price += item_price
            # items_text += f"{i}. {product_name}\n\t\t\t\t{item.count} x {item.price:,.0f} = {item_price:,.0f} so'm\n\n"
            items_text.append(
                i18n.cart.item(
                    i=i,
                    product_name=product_name,
                    count=item.count,
                    price=item.price,
                    item_price=item_price,
                )
            )

        text = i18n.cart.info(products="".join(items_text), total_price=total_price)
        keyboard = await self.cart_keyboard(update, context)
        if not edit:

            new_message = await tg_user.send_message(
                text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            temp.message_id = new_message.message_id
            temp.save()
        else:
            message: Message = update.callback_query.message

            await message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

        return CART

    async def cart_clear(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        items = cart.items.all()

        items.delete()

        return await self.cart(update, context)

    async def cart_set_count(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        _, action, itemId = update.callback_query.data.split(":")

        item = user.cart.items.filter(id=itemId).first()

        if item is None:
            # TODO: Impelement error text
            await update.callback_query.answer()
            return

        item.count += 1 if action == "increase" else -1
        item.save()

        return await self.cart(update, context, True)

    async def cart_remove_item(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        action, itemId = update.callback_query.data.split(":")

        item = user.cart.items.filter(id=itemId).first()

        if item is None:
            # TODO: Impelement error text
            await update.callback_query.answer()
            return

        item.delete()

        return await self.cart(update, context, True)

    def back_from_cart(self, callback: Callable):
        async def wrap(update: UPD, context: CTX):
            tg_user, user, temp, i18n = User.get(update)

            # Prioritize callback first
            result = await callback(update, context)

            # Execute both delete_message calls concurrently
            await self.delete_messages(update, context)

            return result

        return wrap

    async def delete_messages(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        try:
            await asyncio.gather(
                tg_user.delete_message(temp.message_id), tg_user.delete_message(temp.message_id2)
            )
        except Exception as e:
            print(e)

    async def cart_done(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.promocode = None
        cart.time = None
        cart.filial = None
        cart.location = None
        cart.save()

        # await tg_user.send_message(
        #     i18n.time.deliver(),
        #     reply_markup=ReplyKeyboardMarkup(
        #         [
        #             [
        #                 i18n.time.asap(),
        #             ],
        #             [i18n.time.later()],
        #         ]
        #     ),
        #     parse_mode="HTML",
        # )
        # return CART_TIME
        
        await tg_user.send_message(
            i18n.cart.get_method(),
            reply_markup=ReplyKeyboardMarkup(
                [[i18n.cart.deliver(), i18n.cart.take_away()]]
            ),
            parse_mode="HTML",
        )
        print("Menu")

        return CART_GET_METHOD
    
    
    
    
    async def cart_get_method_deliver(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.delivery = "DELIVER"
        cart.save()

        await tg_user.send_message(
            i18n.deliver.location.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton(i18n.buttons.location(), request_location=True)],
                    [i18n.buttons.my_locations()],
                ]
            ),
            parse_mode="HTML",
        )
        return DELIVERY_LOCATION

    async def cart_delivery_location(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        location = update.message.location

        nominatim = Nominatim(user_agent="Google")

        address = nominatim.reverse(f"{location.latitude},{location.longitude}")

        new_location = user.locations.create(
            name=str(address),
            latitude=location.latitude,
            longitude=location.longitude,
            address=str(address),
        )

        temp.location = new_location
        temp.save()

        await tg_user.send_message(
            i18n.deliver.location.confirm(address=address),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        KeyboardButton(
                            i18n.deliver.location.resend(), request_location=True
                        )
                    ],
                    [i18n.buttons.confirm()],
                ]
            ),
            parse_mode="HTML",
        )

        return CART_DELIVER_LOCATION_CONFIRM

    async def cart_deliver_location_confirm(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.location = temp.location
        
        filial: Filial | None = Filial.get_nearest_filial(cart.location)
        cart.filial = filial
        cart.save()
        

        # await tg_user.send_message(
        #     i18n.time.deliver(),
        #     reply_markup=ReplyKeyboardMarkup(
        #         [
        #             [
        #                 i18n.time.asap(),
        #             ],
        #             [i18n.time.later()],
        #         ]
        #     ),
        #     parse_mode="HTML",
        # )
        # return CART_TIME

        # await tg_user.send_message(
        #     i18n.menu.welcome(),
        #     reply_markup=ReplyKeyboardMarkup(
        #         [
        #             [i18n.menu.cart() if user.cart.items.count() > 0 else ""],
        #             *distribute(
        #                 [
        #                     i18n.get_name(category)
        #                     for category in Category.objects.filter(parent=None)
        #                 ],
        #             ),
        #         ]
        #     ),
        #     parse_mode="HTML",
        # )
        # return MENU_CATEGORY

    async def cart_get_method_take_away(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.delivery = "TAKEAWAY"
        cart.save()

        filials = Filial.objects.filter(active=True)

        await tg_user.send_message(
            i18n.takeaway.filial.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        KeyboardButton(
                            i18n.takeaway.filial.check_nearest_filial(),
                            request_location=True,
                        )
                    ],
                    *distribute([i18n.get_name(filial) for filial in filials]),
                ]
            ),
            parse_mode="HTML",
        )

        return CART_TAKEAWAY_FILIAL

    async def cart_takeaway_filial_location(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        location = update.message.location

        filial: Filial | None = Filial.get_nearest_filial(location)

        filials = Filial.objects.filter(active=True)

        await tg_user.send_message(
            i18n.takeaway.filial.filial_info(filial=i18n.get_name(filial)),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [i18n.takeaway.filial.check_nearest_filial()],
                    *distribute([i18n.get_name(filial) for filial in filials]),
                ]
            ),
            parse_mode="HTML",
        )

    async def cart_takeaway_filial(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        filial = Filial.objects.filter(i18n.filter_name(update.message.text)).first()

        if filial is None:
            await tg_user.send_message(
                i18n.takeaway.filial.not_found(), parse_mode="HTML"
            )
            return await self.cart_get_method_take_away(update, context)

        cart = user.cart

        cart.filial = filial
        cart.save()
        
        await tg_user.send_message(
            i18n.time.deliver(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        i18n.time.asap(),
                    ],
                    [i18n.time.later()],
                ]
            ),
            parse_mode="HTML",
        )
        return CART_TIME

        # await tg_user.send_message(
        #     i18n.menu.welcome(),
        #     reply_markup=ReplyKeyboardMarkup(
        #         [
        #             [i18n.menu.cart() if user.cart.items.count() > 0 else ""],
        #             *distribute(
        #                 [
        #                     i18n.get_name(category)
        #                     for category in Category.objects.filter(parent=None)
        #                 ],
        #             ),
        #         ]
        #     ),
        #     parse_mode="HTML",
        # )
        # return MENU_CATEGORY
    
    
    
    

    async def cart_time(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        if update.message.text == i18n.time.later():
            times = get_later_times()
            text = (
                i18n.time.ask_later_deliver()
                if cart.delivery == "DELIVER"
                else i18n.time.ask_later_takeaway()
            )

            await tg_user.send_message(
                text,
                reply_markup=ReplyKeyboardMarkup(
                    distribute([time.strftime("%H:%M") for time in times])
                ),
                parse_mode="HTML",
            )
            return CART_TIME_LATER_TIME

        if update.message.text == i18n.time.asap():
            await tg_user.send_message(
                i18n.data.phone_number.ask(),
                reply_markup=ReplyKeyboardMarkup(
                    [
                        [
                            KeyboardButton(
                                i18n.buttons.phone_number(), request_contact=True
                            )
                        ]
                    ]
                ),
                parse_mode="HTML"
            )
            return CART_PHONE_NUMBER

        await tg_user.send_message(i18n.time.wrong(), parse_mode="HTML")
        return CART_TIME_LATER_TIME

    async def cart_time_later_time(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        time_t = update.message.text

        # Parse the time string into a datetime object, ensuring it's interpreted as today's date
        time = datetime.combine(date.today(), datetime.strptime(time_t, "%H:%M").time())

        time = time if time > datetime.now() else time + timedelta(days=1)

        print(time)

        # temp.time = time
        # temp.save()
        cart = user.cart
        cart.time = time
        cart.save()

        await tg_user.send_message(
            i18n.data.phone_number.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(i18n.buttons.phone_number(), request_contact=True)]]
            ),
            parse_mode="HTML"
        )
        return CART_PHONE_NUMBER

    async def cart_time_asap(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(
            i18n.data.phone_number.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(i18n.buttons.phone_number(), request_contact=True)]]
            ),
            parse_mode="HTML"
        )
        return CART_PHONE_NUMBER

    async def cart_phone_number(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        phone = (
            update.message.contact.phone_number
            if update.message.contact
            else update.message.text
        )

        print(phone)

        cart = user.cart
        cart.phone_number = phone
        cart.save()

        await tg_user.send_message(
            i18n.order.comment.ask(),
            reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
            parse_mode="HTML"
        )
        return CART_COMMENT

    async def cart_comment(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart
        cart.comment = (
            update.message.text if update.message.text != i18n.buttons.skip() else None
        )

        cart.save()

        await tg_user.send_message(
            i18n.order.promocode.ask(),
            reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
            parse_mode="HTML"
        )

        return CART_PROMOCODE

    async def cart_promocode(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        if update.message.text != i18n.buttons.skip():

            promocode = Promocode.objects.filter(code__iexact=update.message.text,
                                                 end_date__gte=timezone.now()
                                                 ).first()

            if promocode is None:
                await tg_user.send_message(
                    i18n.order.promocode.not_found(),
                    reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
                    parse_mode="HTML"
                )
                return CART_PROMOCODE

            used = user.carts.filter(promocode=promocode).exists()

            if used:
                await tg_user.send_message(
                    i18n.order.promocode.used(),
                    reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
                    parse_mode="HTML"
                )
                return CART_PROMOCODE

            if promocode.orders.count() >= promocode.count:
                await tg_user.send_message(
                    i18n.order.promocode.ended(),
                    reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
                    parse_mode="HTML"
                )

                return CART_PROMOCODE

            if promocode.min_amount > 0 and promocode.min_amount > cart.price:
                await tg_user.send_message(
                    i18n.order.promocode.min_amount(amount=promocode.min_amount),
                    reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
                    parse_mode="HTML"
                )
                return CART_PROMOCODE

            if 0 < promocode.max_amount < cart.price:
                await tg_user.send_message(
                    i18n.order.promocode.min_amount(amount=promocode.max_amount),
                    reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
                    parse_mode="HTML"
                )
                return CART_PROMOCODE

            cart.promocode = promocode
            cart.save()

        products_text = []

        for i, item in enumerate(cart.items.all(), 1):
            products_text.append(
                (
                    f"{i}. {i18n.get_name(obj=item.product)}\n"
                    f"{item.count} x {item.price} = {item.count * item.price}"
                )
            )

        await tg_user.send_message(
            i18n.order.info.base(
                name=user.name,
                number=cart.phone_number,
                delivery_method=cart.delivery,
                comment=i18n.order.info.comment(comment=cart.comment) if cart.comment else "",
                promocode=i18n.order.info.promocode(name=cart.promocode.name, amount=cart.promocode.amount,
                                                    measurement="%" if cart.promocode.measurement == "PERCENT" else "so'm") if cart.promocode else "",
                filial=i18n.get_name(cart.filial),
                total_price=cart.discount_price,
                orders="\n".join(products_text),
            ),
            reply_markup=ReplyKeyboardMarkup(
                [[i18n.buttons.confirm(), i18n.buttons.cancel()]]
            ),
            parse_mode="HTML"
        )

        return CART_CONFIRM

    async def cart_reject(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message("Rad etildi qilindi.", parse_mode="HTML")

        return await self.cart(update, context)

    async def cart_confirm(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(
            i18n.payment.method.ask(),
            reply_markup=ReplyKeyboardMarkup([
                [
                    i18n.payment.click(),
                    i18n.payment.payme()
                ],
                [
                    i18n.payment.cash()
                ]
            ]),
            parse_mode="HTML"
        )
        return PAYMENT_METHOD

    async def cart_payment_method(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        methods = {
            i18n.payment.click(): CLICK,
            i18n.payment.payme(): PAYME,
            i18n.payment.cash(): CASH
        }

        method = methods.get(update.message.text)

        if method is None:
            await tg_user.send_message(i18n.payment.method.not_found(), reply_markup=ReplyKeyboardMarkup([
                [
                    i18n.payment.click(),
                    i18n.payment.payme()
                ],
                [
                    i18n.payment.cash()
                ]
            ]), parse_mode="HTML")

            return PAYMENT_METHOD

        cart = user.cart

        products = [
            LabeledPrice(i18n.get_name(item.product), int((item.count * item.price) * 100)) for item in cart.items.all()
        ]
        if cart.promocode:
            print(cart.saving * 100)
            products.append(
                LabeledPrice(
                    "Promocode",
                    -int(cart.saving * 100),
                )
            )

        if method in [CLICK, PAYME]:
            cart.status = "PENDING_PAYMENT"
            cart.save()
            await tg_user.send_invoice(
                i18n.payment.title(),
                i18n.payment.description(),
                f"cart:{base64.b64encode(f"{cart.id}".encode()).decode()}:{method}",
                self.CLICK_TOKEN if method == CLICK else self.PAYME_TOKEN,
                "UZS",
                products,
                reply_markup=InlineKeyboardMarkup([
                    InlineKeyboardButton("To'lash",pay=True)
                ],[
                    InlineKeyboardButton(i18n.buttons.back(),callback_data="back")
                ])
            )
            return CART_PAYMENT
        else:
            cart.order_time = timezone.now()
            cart.status = "PENDING"
            cart.save()
            
            
            
            order = cart.order(self.iiko_manager)
            
            # if order:
            #     await tg_user.send_message("Buyurtma iikoga yuborildi.")
            # else:
            #     await tg_user.send_message("Buyurtma iikoga yuborilmadi.")
            
            
            await tg_user.send_message(i18n.payment.done(), parse_mode="HTML")
            
            
            return await self.start(update,context)

    
    
    async def back_from_cart_payment(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)
        
        
        try:
            await update.message.delete()
        except Exception as e:
            print(e)
            pass

        await tgUser.send_message(i18n.payment.method.not_found(), reply_markup=ReplyKeyboardMarkup([
                [
                    i18n.payment.click(),
                    i18n.payment.payme()
                ],
                [
                    i18n.payment.cash()
                ]
            ]), parse_mode="HTML")

        return PAYMENT_METHOD
