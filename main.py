import sys

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader


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
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
scene.fog_density = (1, 128)
sky = Sky()
ground = Entity(model='plane', collider='box', scale=640, texture='grass', texture_scale=(30,30))

#зрение от первого лица и игрок:
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-10, color=color.cyan, origin_y=-0.5, speed=8, collider='box')
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

#Ui настроек (пока не работает)

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
        Button(text="Close menu", color=color.dark_gray, on_click=apply_settings),
        Button(text="Exit", color=color.red, on_click=ExitButton),
    ), position=(0, 0))
    FullScreenMode = settings_panel.content[1]
    FullScreenMode.on_value_changed = toggle_fullscreen
    return settings_panel, FullScreenMode

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
    #switch_camera(key)


app.run() #Старт игры