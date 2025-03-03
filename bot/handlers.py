import asyncio
import time


from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import Keyboards as kb
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from bot.db import get_item, get_name, get_id, insert_data, add_req, get_basket_info, get_basket_card, get_user_info, \
    get_category_list, add_item, get_category_with_name, add_new_category, get_items, delete_item_bd, get_itemsos, \
    add_basket_bool

router = Router()



class Reg(StatesGroup):
    id = State()
    name = State()
    number = State()
    location = State()




@router.message(CommandStart())
async def StartButton(message:Message, state: FSMContext):
    tg_name = get_id(message.from_user.id)
    if tg_name is None:
        await message.answer("""
                Добро пожаловать в онлайн магазин Stomdiscont! Давайте пройдем небольшую регистрацию!\n\n
                Введите ваше имя!
                """)

        await state.update_data(id=message.from_user.id)
        await state.set_state(Reg.name)

    else:
        await message.answer("""
        \t\t\tStomdiscont\n\n
        Стоматологические товары по низким ценам!
        """,reply_markup=kb.main)
@router.message(Reg.name)
async def add_name(message:Message, state: FSMContext):
    data = message.text


    await state.update_data(name=data)
    await state.set_state(Reg.number)
    await message.answer('Введите ваш номер телефона по которому мы сможем с вами связаться, после того как вы сделаете заказ')

@router.message(Reg.number)
async def add_number(message: Message, state: FSMContext):
    data = message.text

    await state.update_data(number=data)
    await state.set_state(Reg.location)
    await message.answer(
        'Отлично, теперь введите свой адрес для того чтобы наши скоростные курьеры доставили ваш заказ!')

@router.message(Reg.location)
async def add_location(message: Message, state: FSMContext):
    location = message.text
    await state.update_data(location=location)


    data_all = await state.get_data()
    number = data_all['number']
    name = data_all['name']
    tg_id = data_all['id']

    insert_data(tg_id, name, number, location)


    await message.answer(f'Отлично, вот ваши данные:\nИмя: {name}\nНомер телефона: {number}\nАдрес: {location}')
    await state.clear()
    await message.answer("""
    \t\t\tStomdiscont\n\n
        Стоматологические товары по низким ценам!
            """, reply_markup=kb.main)

# class AS(StatesGroup):
#     waiting_for_password = State()

@router.message(Command('admin'))
async def admin_but(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
               InlineKeyboardButton(text='Настройка товаров и категорий', callback_data='settings')
            ],
            [InlineKeyboardButton(text='Заявки', callback_data='reqe')]
        ])
    keyboard_false = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Вернуться', callback_data='to_main')
        ]
    ])
    if message.from_user.id == int('873034839') or int('256365981'):
        await message.delete()

        await message.answer('Админ меню\nВыберите действие', reply_markup=keyboard)
    else:
        await message.answer('❌У вас нет доступа к Админ-меню❌', reply_markup=keyboard_false)
        # await state.set_state(AS.waiting_for_password)       Старая тема


# @router.message(AS.waiting_for_password)
# async def password_check(message:Message, state: FSMContext):
#     data = message.text
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(text='Настройка товаров и категорий', callback_data='settings')
#         ],
#         [InlineKeyboardButton(text='Заявки', callback_data='reqe')]
#     ])
#     if data == '123':
#         await message.answer('Админ меню\nВыберите действие', reply_markup=keyboard)
#         await state.clear()
#     else:
#         await message.answer('пароль неверный, повторите попытку, либо введите команду /c')



@router.message(Command('c'))
async def cancel_command(message: Message, state: FSMContext):
    await message.answer("""
                    \t\t\tStomdiscont\n\n
        Стоматологические товары по низким ценам!
                """, reply_markup=kb.main)
    await state.clear()




@router.message(F.text == 'Каталог')
async def Catalog_button(message:Message):
    await message.answer("Выберите категорию товара", reply_markup=kb.categories())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery, state: FSMContext):
    try:
        category_id = callback.data.split('_')[1]               # Получаем из callback_query ID категории.
        await callback.answer('Вы выбрали категорию')
        ud = await state.get_data()
        if "basket" not in ud:                                  # Проверяем, есть ли у нас в state корзина. state это не только FSM, а и локальная база данных, привязанная к одномц пользоваелю.
            await state.update_data(basket={})
        await callback.message.edit_text('Выберите товар по категории', reply_markup=kb.items(category_id))
    except Exception as e:
        await callback.answer(f"Ошибка: {e}")
        print(f"Exception in category handler: {e}")


@router.callback_query(F.data == 'back')
async def to_back_page(callback:CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Выберите категорию товара', reply_markup=kb.categories())


@router.callback_query(F.data == 'to_main')
async def to_main_page(callback:CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("""
                    \t\t\tStomdiscont\n\n
        Стоматологические товары по низким ценам!
    """, reply_markup=kb.main)


@router.callback_query(F.data.startswith('item_'))
async def category(callback: CallbackQuery, state: FSMContext):
    item_id = callback.data.split('_')[1]  # Получаем из callback_query ID товара
    item_data = get_item(item_id)
    await callback.answer('Вы выбрали товар')

    ud = await state.get_data() # получаем данные из state

    if item_id in ud["basket"]:     # если данный товар есть, то мы можем его убрать (добавили кнопку минус), в ином случае, только добавить в корзину есть
        bskt = ud['basket']
        amount = bskt[item_id]["amount"]
        add_to_basket = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='+', callback_data=f'add_basket-{item_id}'),
                    InlineKeyboardButton(text='-', callback_data=f'delete_basket-{item_id}')
                ],
                [
                    InlineKeyboardButton(text='Убрать из корзины', callback_data=f'clear_item-{item_id}')
                ],
                [
                    InlineKeyboardButton(text='На главную', callback_data='to_main')
                ]
            ]
        )
        await callback.message.edit_text(
            f'Название: {item_data[1]}\nОписание: {item_data[2]}\nЦена: {item_data[3]}р\nКоличество: {amount}',
            reply_markup=add_to_basket
        )
    else:
        add_to_basket = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Выбрать товар', callback_data=f'add_basket-{item_id}')
                ],
                [
                    InlineKeyboardButton(text='На главную', callback_data='to_main')
                ]
            ]
        )


        await callback.message.edit_text(
          f'Название: {item_data[1]}\nОписание: {item_data[2]}\nЦена: {item_data[3]}р',
           reply_markup=add_to_basket
        )

@router.callback_query(F.data.startswith('clear_item'))
async def clear_item(callback:CallbackQuery, state: FSMContext):
    item_id = callback.data.split('-')[1]
    item_data = get_item(item_id)
    ud = await state.get_data()
    keyboard_in = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Выбрать товар', callback_data=f'add_basket-{item_id}')
        ],
        [
            InlineKeyboardButton(text='На главную', callback_data='to_main')
        ]
    ]
    )

    bskt = ud['basket']
    del bskt[item_id]
    await state.update_data(basket=bskt)
    await callback.answer('товар удален из корзины')
    await callback.message.edit_text(f'Название: {item_data[1]}\nОписание: {item_data[2]}\nЦена: {item_data[3]}р',
        reply_markup=keyboard_in)



@router.callback_query(F.data.startswith('add_basket'))
async def add_basket_b(callback:CallbackQuery, state: FSMContext):
    item_id = callback.data.split("-")[1]
    item_data = get_item(item_id)
    ud = await state.get_data()  # получили данные из state
    bskt = ud.get("basket", {})  # Безопасное получение корзины

    item_id = str(item_id)
    if item_id in ud["basket"]: # проверяем наличие товара, если есть в корзине, то добавляем, если нет, то создаем под него ключ. все данные в state хранятся в виде словаря (ключ - значение) (база данных называется - Redis)
        bskt[item_id]['amount'] += 1
    else:
        bskt[item_id] = {'name': item_data[1], 'amount': 1}
    await state.update_data(basket=bskt)


    total_amount = 0  # переменная для суммирования количества
    for item_info in bskt.values():  # итерируем только по значениям
        if item_info['name'] == item_data[1]:
            total_amount += item_info['amount']

    backet = str(total_amount)
    await callback.answer('Товар в корзине!')
    keyboard_in = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='+', callback_data=f'add_basket-{item_id}'),
            InlineKeyboardButton(text='-', callback_data=f'delete_basket-{item_id}')],
        [
            InlineKeyboardButton(text='Убрать из корзины', callback_data=f'clear_item-{item_id}')
        ],
        [
            InlineKeyboardButton(text='На главную', callback_data='to_main')
        ]

    ])
    await callback.message.edit_text(f'Название: {item_data[1]}\nОписание: {item_data[2]}\nЦена: {item_data[3]}р\nКоличество: {int(backet)}', reply_markup=keyboard_in)



@router.callback_query(F.data.startswith('delete_basket'))
async def delete_basket_b(callback:CallbackQuery, state: FSMContext):
    # здесь аналогично add_basket_b, только мы уверены на 100 проц, что товар есть
    item_id = callback.data.split("-")[1]
    item_data = get_item(item_id)
    ud = await state.get_data()
    bskt = ud["basket"]
    keyboard_in = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='+', callback_data=f'add_basket-{item_id}'),
            InlineKeyboardButton(text='-', callback_data=f'delete_basket-{item_id}')],
        [
            InlineKeyboardButton(text='Убрать из корзины', callback_data=f'clear_item-{item_id}')
        ],
        [
            InlineKeyboardButton(text='На главную', callback_data='to_main')
        ]

    ])
    if bskt[item_id]['amount'] > 1:
        bskt[item_id]['amount'] -= 1
        await state.update_data(basket=bskt)
        backet = ''
        total_amount = 0  # переменная для суммирования количества
        for item_info in bskt.values():  # итерируем только по значениям
            if item_info['name'] == item_data[1]:
                total_amount += item_info['amount']
                backet = total_amount
        await callback.message.edit_text(
            f'Название: {item_data[1]}\nОписание: {item_data[2]}\nЦена: {item_data[3]}р\nКоличество: {backet}',
            reply_markup=keyboard_in)
    else:
        await callback.answer('Нельзя сделать меньше единицы')



                                                #ОТПРАВЛЕНИЕ ЗАЯВКИ НА ПОКУПКУ
@router.callback_query(F.data == 'send_req')
async def accept_req(callback: CallbackQuery, state: FSMContext):

    try:
        await callback.message.edit_text('ваша заявка успешно отправлена!')

        data = await state.get_data()
        bool_info = "True"
        for item_id, item_data in data['basket'].items():
            dt = get_item(item_id)
            amount = int(item_data['amount'])


            count = dt[3]
            tg_id = callback.from_user.id

            item_name = dt[1]
            description = dt[2]

            add_req(tg_id, count, item_name, description, amount, bool_info)
        await state.clear()

    except:

        await callback.message.edit_text('Проблемы с сервером повторите попытку позже')


#                               ХЭНДЛЕР НА ПРОСМОТР ЗАКАЗОВ

@router.callback_query(F.data == 'reqe')
async def reqe(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Активные', callback_data='active_req'),
            InlineKeyboardButton(text='Архив', callback_data='unactive_req')
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='admin_menu')
        ]
    ])

    await callback.message.edit_text('Просмотр', reply_markup=keyboard)

@router.callback_query(F.data == 'active_req')
async def active_req_kb(callback: CallbackQuery):
    all_items = get_basket_info()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    if all_items is not None:
        for item in all_items:
            if item[6] == 'True':
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(text=f"Заявка - {item[0]}", callback_data=f'requests={item[0]}={item[5]}')
                ])
            else:
                pass
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text='Назад', callback_data='reqe')
        ])
        await callback.message.edit_text('Заявки: ', reply_markup=keyboard)
    else:
        new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Вернуться', callback_data='show_menu')
            ]
        ])

        await callback.message.edit_text('Заявок нет', reply_markup=new_keyboard)


@router.callback_query(F.data == 'unactive_req')
async def unactive_req_kb(callback: CallbackQuery):
    all_items = get_basket_info()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    if all_items is not None:
        for item in all_items:
            if item[6] == 'False':
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(text=f"Заявка - {item[0]}", callback_data=f'requests={item[0]}={item[5]}')
                ])
            else:
                pass
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text='Назад', callback_data='reqe')
        ])
        await callback.message.edit_text('Заявки: ', reply_markup=keyboard)

    else:
        new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Вернуться', callback_data='show_menu')
            ]
        ])

        await callback.message.edit_text('Заявок нет', reply_markup=new_keyboard)


#                               КНОПКА ВЕРНУТЬСЯ В АДМИН МЕНЮ

@router.callback_query(F.data == 'admin_menu')
async def admin_menu(callback: CallbackQuery):
    await callback.message.edit_text('Админ меню\nВыберите действие', reply_markup=kb.admin_but)

@router.callback_query(F.data.startswith('requests'))
async def item_check_admin(callback: CallbackQuery):
    try:
        card = callback.data.split('=')[1]
        item_data = get_basket_card(card)
        user_data = callback.data.split('=')[2]
        user_list = get_user_info(user_data)
        user = user_list[0]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Назад', callback_data='reqe')
            ],
            [
                InlineKeyboardButton(text='Выполнен', callback_data=f'accepted-{card}')
            ]
        ])
        item_tuple = item_data[0]
        price = int(item_tuple[3])
        quantity = int(item_tuple[1])
        sum_items = price * quantity
        await callback.message.edit_text(f'Товар: {item_tuple[2]}\nКоличество: {quantity}\n\nКлиент: {user[2]}\nНомер телефона: {user[4]}\nАдрес: {user[3]}\n\n\nИтог: {sum_items}', reply_markup=keyboard)
    except:
        pass

@router.callback_query(F.data.startswith == 'accepted')
async def accepted(callback: CallbackQuery):
    data = callback.data.split('-')[1]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Активные', callback_data='active_req'),
            InlineKeyboardButton(text='Архив', callback_data='unactive_req')
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='admin_menu')
        ]
    ])
    success = add_basket_bool(data)
    if success:
        await callback.message.edit_text('Выбор действия', reply_markup=keyboard)
    else:
        await callback.answer('Не вышло, попробуйте еще раз')
@router.callback_query(F.data == "clear_basket")
async def clear_bascket(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Корзина очищена")
    await callback.message.delete()
    await callback.message.answer("""
                    \t\t\tStomdiscont\n\n
        Стоматологические товары по низким ценам!
    """, reply_markup=kb.main)

@router.message(F.text == 'Корзина')
async def basket(message: Message, state: FSMContext):
    ud = await state.get_data()
    try:

        output_data = ''
        bskt = ud['basket']
        for info_id, item_info in bskt.items():

            output_data += f"{item_info['name']}: Количество: {item_info['amount']}\n"
    
        if ud['basket']:

            await message.answer(f'Корзина:\n\n{output_data}', reply_markup=kb.back_from_basket_true)
        else:
            await message.answer('Корзина пуста!\nПерейдите в каталог и выберите товары', reply_markup=kb.back_from_basket)
    except:
        await message.answer('Корзина пуста!\nПерейдите в каталог и выберите товары', reply_markup=kb.back_from_basket)

class Product(StatesGroup):
    name = State()
    description = State()
    price = State()
    categories = State()

#                                   ДОБАВЛЕНИЕ ТОВАРА В АДМИН МЕНЮ

@router.callback_query(F.data == 'add_product')
async def add_product_admin(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text('Введите название:', reply_markup=kb.cancel)
        await state.set_state(Product.name)

@router.callback_query(F.data == 'cancel_d')
async def c_a(callback: CallbackQuery, state: FSMContext):
    ud = await state.get_data()



    await state.clear()
    await callback.message.edit_text('Админ меню\nВыберите действие', reply_markup=kb.admin_but)

@router.callback_query(F.data == 'back_com')
async def back_com(callback: CallbackQuery):
    await callback.message.edit_text('Админ меню\nВыберите действие', reply_markup=kb.admin_but)

@router.message(Product.name)
async def name_product(message: Message, state: FSMContext):

    name = message.text
    await state.update_data(name=name)
    await state.set_state(Product.description)
    await message.reply('Отлично, теперь введите описание:', reply_markup=kb.cancel)
@router.message(Product.description)
async def description_product(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await state.set_state(Product.price)
    await message.reply('Сколько будет стоить? Введите цену:', reply_markup=kb.cancel)

@router.message(Product.price)
async def price_product(message:Message, state: FSMContext):
    price = message.text
    await state.update_data(price=price)
    await state.set_state(Product.categories)

    all_categories = get_category_list()
    couple_list_names = []

    for item in all_categories:
        couple_list_names.append(item[1])


    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for ct in couple_list_names:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=ct, callback_data=f'ct-{ct}')])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text='Отменить', callback_data='cancel_d')
    ])
    await message.reply('В какую категорию будет входить этот товар?', reply_markup=keyboard)



@router.callback_query(F.data.startswith('ct'), Product.categories)
async def category_product(callback: CallbackQuery, state: FSMContext):
    try:
        category_name = callback.data.split('-')[1]
        category_id = get_category_with_name(category_name)

        if category_id is None:
            await callback.answer("Ошибка: категория не найдена.")
            return

        info = await state.get_data()
        name = info['name']
        description = info['description']
        price = float(info['price'])

        add_item(name, description, price, category_id)
        await callback.message.answer("Товар успешно добавлен!")

        await callback.message.delete()

        await state.clear()

        await callback.message.answer('Выбор действия', reply_markup=kb.settings)

    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        await callback.answer("Произошла ошибка при добавлении товара.")


#                                       ОБРАБОТЧИК settings
@router.callback_query(F.data == 'settings')
async def settings(callback: CallbackQuery):
    await callback.message.edit_text('Выбор действия', reply_markup=kb.settings)

#                                       ДОБАВЛЕНИЕ КАТЕГОРИИ

class NewCategory(StatesGroup):
    name = State()

@router.callback_query(F.data == 'add_new_category')
async def add_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите название категории', reply_markup=kb.cancel)
    await state.set_state(NewCategory.name)

@router.message(NewCategory.name)
async def name_category(message: Message, state: FSMContext):
    data = message.text
    all_categories = get_category_list()
    len_ca = len(all_categories)
    new_id = len_ca + 1


    add_new_category(new_id, data)

    await message.answer('Категория успешно добавлена!')
    await message.answer('Выбор действия', reply_markup=kb.settings)


#                                               Удаление товара

@router.callback_query(F.data == 'delete_item')
async def delete_item(callback: CallbackQuery):
    items = get_items()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for item in items:
        item_name = item[1]
        item_id = item[0]
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=item_name, callback_data=f'del_item-{item_id}')])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text='Отменить', callback_data='back_com')
    ])
    await callback.message.edit_text('Какой товар вы хотите удалить', reply_markup=keyboard)

@router.callback_query(F.data == 'del_item')
async def delete_select_item(callback: CallbackQuery):
    data = callback.data.split('-')[1]
    success = delete_item_bd(data)
    if success:
        await callback.message.answer('Товар удален')
        await callback.message.answer('Выбор действия', reply_markup=kb.settings)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Попробывать еще', callback_data='delete_item')
            ],
            [
                InlineKeyboardButton(text='Выйти в главное меню', callback_data='back_com')
            ]
        ])
        await callback.message.answer('Товар не был удален', reply_markup=keyboard)

#                                               ПРОСМОТР ТОВАРОВ И КАТЕГОРИЙ

@router.callback_query(F.data == 'show_menu')
async def view_items(callback: CallbackQuery):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Товары', callback_data='view_items')
        ],
        [
            InlineKeyboardButton(text='Категории', callback_data='view_categories')
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='back_com')
        ]
    ])

    await callback.message.edit_text('Выбор действия', reply_markup=keyboard)

@router.callback_query(F.data == 'view_items')
async def view_items(callback: CallbackQuery):
    categories = get_itemsos()


    items_with_prices = [f'Название: {item[1]} Цена: {item[3]}' for item in categories]
    empt = '\n\n'.join(items_with_prices)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Выйти в главное меню', callback_data='back_com')]
    ])
    await callback.message.edit_text(f'{empt}', reply_markup=keyboard)


@router.callback_query(F.data == 'view_categories')
async def view_categories(callback: CallbackQuery):
    categories = get_category_list()
    item_list = [item[1] for item in categories]
    empt = '\n\n'.join([f'Название: {name}' for name in item_list])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Выйти в главное меню', callback_data='back_com')]
    ])

    try:
        await callback.message.edit_text(f'{empt}', reply_markup=keyboard)
    except aiogram.exceptions.MessageCantBeEdited:
        await callback.message.answer(f'{empt}', reply_markup=keyboard)
    except aiogram.exceptions.TelegramBadRequest as e:
        await callback.answer(f"Ошибка: {e}")



