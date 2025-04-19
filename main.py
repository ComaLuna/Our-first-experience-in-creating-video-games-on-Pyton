import sys
from sys import orig_argv
from PIL.DdsImagePlugin import module
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from numpy import floor
from perlin_noise import PerlinNoise #Шум перлина дужен для генерации(ОН НЕ БЕСПОЛЕЗЕН)


#Окно игры:
app = Ursina(
    title='Name',
    fps_counter=False,
    vsync=True,
    entity_counter=False,
    development_mode=False,
    icon='assets/Myfirstgame.ico'
)

#Шейдер
Entity.default_shader = lit_with_shadows_shader

#Переменые: (их пока нет)
#Модельки мира
#sun = DirectionalLight()
# sun.look_at(Vec3(1, -1, 0))
scene.fog_density = (1, 30)
sky = Sky()
# ground = Entity(model='plane', collider='box', scale=640, texture='grass', texture_scale=(30,30))

#зрение от первого лица и игрок:
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', color=color.cyan, origin_y=-0.5, speed=8, collider='box')
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

#Ui настроек
def toggleSettingPanel():
    settings_panel.enabled = not settings_panel.enabled

def create_settings_panel():
    def apply_settings():
        settings_panel.enabled = False  # Закрываем панель после применения настроек
    def ExitButton():
        sys.exit()

    settings_panel = WindowPanel(title="Settings", content=(
        Text("Full screen:"),
        Slider(min=0, max=1, step = 1, default=1, color=color.azure, dynamic=False),
        # Text("World size:"),
        # Slider(min=30, max=45, step=1, default=30, color=color.azure, dynamic=False),
        Button(text="Close menu", color=color.dark_gray, on_click=apply_settings),
        Button(text="Exit", color=color.red, on_click=ExitButton),
    ), position=(0, 0))
    FullScreenMode = settings_panel.content[1]
    FullScreenMode.on_value_changed = toggle_fullscreen
    # WorldSize = settings_panel.content[3]
    # WorldSize.on_value_changed = ChangeWorldSize
    return settings_panel, FullScreenMode

# def ChangeWorldSize(WorldSize):
#     global terrain_width
#     terrain_width = WorldSize

def toggle_fullscreen(): #Код на изменения фулл скрина
    if FullScreenMode.value > 0.5:
        window.fullscreen = True
    else:
        window.fullscreen = False

b = Button(parent=camera.ui, icon='assets\settings.png', color=color.black, scale=0.09, x=-0.84, y=0.45)
b._on_click = toggleSettingPanel
settings_panel, FullScreenMode = create_settings_panel()
settings_panel.enabled = False

#Функции для биндов
# Разблокировка мыши по нажатию клавиши:
def mouselocker(key):
    if key == 'left alt':
        mouse.locked = not mouse.locked
def esc_Menu(key):
    if key == 'escape':
        settings_panel.enabled = not settings_panel.enabled

#Текстуры
grass_texture = load_texture("assets/textures/grass.png")

class Voxel(Button): #Класс для блоков
    def __init__(self, position=(0, 0, 0), texture=grass_texture): # Определяем конструктор
        super().__init__(
            parent=scene, # Указываем сцену, чтобы объект был виден в игре
            model="assets/models/block", # Указываем модель объекта
            scale=0.5, # Указываем масштаб объекта
            texture=texture, # Указываем текстуру объекта
            position=position, # Указываем позицию объекта
            origin_y=0.5, # Указываем точку опоры объекта
            color=color.color(0, 0, random.uniform(0.9, 1)), # Указываем цвет объекта как случайный оттенок зеленого
        )

#Генерация Мира
noise = PerlinNoise(octaves=2, seed=2025)
amp = 6 #Амплетуда
freq = 24 #Частота
terrain_width = 35 # #Ширина и длина
landscale = [[0 for i in range(terrain_width)] for i in range(terrain_width)]

for position in range(terrain_width**2):
    x = floor(position / terrain_width)
    z = floor(position % terrain_width)
    # Для получения шума Перлина используем метод noise
    y = floor(noise([x / freq, z / freq]) * amp)
    landscale[int(x)][int(z)] = int(y) # Присваиваем значение y в списке landscale по индексам x и z

for x in range(terrain_width):
    for z in range(terrain_width):
        block = Voxel(position=(x, landscale[x][z], z))

# Это в разработке
# Сменя режима камеры с 1го лица на 3тие
# def switch_camera(key):
#     global is_third_person
#     global editor_camera
#     if held_keys['z']:
#         if is_third_person:
#             editor_camera = EditorCamera(enabled=True, ignore_paused=True)
#         else: #Переключение на вид от первого лица
#             editor_camera = EditorCamera(enabled=False, ignore_paused=True)
#         is_third_person = not is_third_person

#Бинды
# Разблокировка мыши по нажатию клавиши:
def input(key):
    mouselocker(key)
    esc_Menu(key)
    revive(key)
    taken_damage_in_jump(key)
    #switch_camera(key)

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
def taken_damage_in_jump(key):
    global health, is_dead
    if key == "r":
        take_damage(0.2)  # Уменьшаем хелбар при нажатии пробела
        
def revive(key):
    global health, is_dead
    if key == "r" and is_dead:
        health = 1.0  # Полностью восстанавливаем здоровье
        health_bar.scale_x = max(health * 0.5, 0.01)  # Минимальный размер (чтобы не пропадал)
        health_bar.color = color.green
        is_dead = False  # Возвращаем игрока к жизни

app.run() #Старт игры