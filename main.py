from sys import orig_argv

from PIL.DdsImagePlugin import module
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader


#Окно игры:
app = Ursina(
    title='Name',
    fps_counter=False,
    vsync=True,
    entity_counter=False,
    icon='assets/Myfirstgame.ico'
)

#Шейдер
Entity.default_shader = lit_with_shadows_shader

#Переменые: (их пока нет)

#Модельки мира
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
sky = Sky()
ground = Entity(model='plane', collider='box', scale=640, texture='grass', texture_scale=(30,30))

#зрение от первого лица и игрок:
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-10, color=color.blue, origin_y=-0.5, speed=8, collider='box')
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))
camera_mode = 'first_person'

#Ui настроек (пока не работает)
b = Button(parent=camera.ui, icon='assets\settings.png', color=color.black, scale=0.09, x=-0.84, y=0.45)
print(b.on_click)

#Функции для биндов
#Разблокировка мыши по нажатию клавиши:
def mouselocker(key):
    if key == 'left alt':
        mouse.locked = not mouse.locked


#Бинды
##Разблокировка мыши по нажатию клавиши:
def input(key):
    mouselocker(key)
    switch_camera(key)





#Это в разработке
def switch_camera(key):
    global camera_mode
    if held_keys['z']:
        if (camera_mode == 'first_person'):
            camera.position = (0, 10, -15)
            camera.rotation_x = 30
            camera_mode = 'third_person'
        else: #Переключение на вид от первого лица
            FirstPersonController(model='cube', z=-10, color=color.blue, origin_y=-0.5, speed=8, collider='box')
            # camera.parent = player
            # camera.position = (0, 1.8, 0)
            # camera.rotation = (0, 0, 0)
            # camera_mode = 'first_person'


#ХЕЛБАР
# Хелбар (индикатор здоровья) в левом нижнем углу
health_bar = Entity(
    parent=camera.ui,  # UI-слой
    model="quad",
    color=color.green,
    scale=(0.5, 0.05),  # Размер
    position=(-0.45, -0.45),  # Перемещаем в левый нижний угол
    origin=(-0.5, 0)  # Точка отсчета слева
)


# Переменные для отслеживания урона и регенерации
health = 1.0  # Текущее здоровье (от 0 до 1)
last_damage_time = 0  # Время последнего урона
regen_rate = 0.01  # Скорость регенерации
regen_delay = 5  # Через сколько секунд начнется регенерация
is_dead = False  # Флаг смерти игрока


# Функция для нанесения урона
def take_damage(amount):
    global health, last_damage_time, is_dead

    if is_dead:  # Если игрок мертв, урон не проходит
        return

    health = max(health - amount, 0)  # Уменьшаем здоровье, но не даем уйти ниже 0
    health_bar.scale_x = max(health * 0.5, 0.01)  # Минимальный размер (чтобы не пропадал)
    last_damage_time = time.time()  # Запоминаем время последнего урона

    if health == 0:
        health_bar.color = color.red  # Если здоровье закончилось
        is_dead = True  # Игрок "умер"


# Функция обновления (каждый кадр)
def update():
    global health, is_dead

    # Если прошло 5 секунд без урона - восстанавливаем здоровье
    if not is_dead and time.time() - last_damage_time > regen_delay and health < 1.0:
        health = min(health + regen_rate, 1.0)  # Увеличиваем здоровье, но не больше 1
        health_bar.scale_x = max(health * 0.5, 0.01)  # Минимальный размер (чтобы не пропадал)

        if health > 0:
            health_bar.color = color.green  # Если началось восстановление, возвращаем цвет


# Функция для респавна (нажмите "R" для возрождения)
def input(key):
    global health, is_dead
    if key == "space":
        take_damage(0.2)  # Уменьшаем хелбар при нажатии пробела

    if key == "r" and is_dead:
        health = 1.0  # Полностью восстанавливаем здоровье
        health_bar.scale_x = max(health * 0.5, 0.01)  # Минимальный размер (чтобы не пропадал)
        health_bar.color = color.green
        is_dead = False  # Возвращаем игрока к жизни



app.run() #Старт игры