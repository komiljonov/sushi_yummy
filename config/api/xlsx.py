from io import BytesIO
from typing import List
from django.http import HttpResponse
import pandas as pd
from data.cart.models import Cart


def generate_excel_from_orders(order_list: List[Cart], res: HttpResponse):

    rows = []

    print(order_list)

    for i, order in enumerate(order_list, 1):

        for j, item in enumerate(order.items.all(), 1):

            row = {
                "№": order.order_id if j == 1 else "",
                "Foydalanuvchi idsi": order.user.chat_id if j == 1 else "",
                "Ismi": order.user.name if j == 1 else "",
                "Telefon raqami": order.phone_number if j == 1 else "",
                "referall": order.user.referral if j == 1 else "",
                "Buyurtma raqami": order.order_id if j == 1 else "",
                "Buyurtma narxi": order.price if j == 1 else "",
                "Yetkazib berish narxi": None if j == 1 else "",
                "Jami narxi": order.price if j == 1 else "",
                "Bitirgan vaqti": order.time.strftime("%d/%m/%Y, %H:%M:%S") if j == 1 else "",
                "Tasdiqlangan vaqti": order.order_time.strftime("%d/%m/%Y, %H:%M:%S") if j == 1 else "",
                "To'lov turi": "Not available" if j == 1 else "",
                "Promocode": order.promocode.code if order.promocode and j == 1 else "",
                "Yetkazib berish turi": "Not available" if j == 1 else "",
                "Filial": order.filial.name_uz if order.filial and j == 1 else "",
                "Mahsulot": item.product.name_uz,
                "Mahsulot narxi": item.price,
                "Mahsulot soni": item.count,
                "Mahsulot jami narxi": (item.price * item.count),
                "Mahsulot qo'shilgan vaqti": order.time.strftime("%d/%m/%Y, %H:%M:%S"),
            }
            # Append the row to the list
            rows.append(row)

    # Create a DataFrame from the rows
    df = pd.DataFrame(rows)


    # Save the DataFrame to an Excel file
    df.to_excel(res, index=False)

    return res
