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
player = FirstPersonController(model='cube', z=-10, color=color.blue, origin_y=-0.5, speed=8, collider='box')
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))
is_third_person = False

#Ui настроек (пока не работает)
# wp = WindowPanel(
#     title='Custom Window',
#     content=(
#         Text('Name:'),
#         InputField(name='name_field'),
#         Button(text='Submit', color=color.azure),
#         Slider(),
#         Slider(),
#         ButtonGroup(('test', 'eslk', 'skffk'))
#     ),
#     popup=False
# )
# wp.enabled = False
# wp.y = wp.panel.scale_y / 2 * wp.scale_y  # center the window panel
# wp.layout()
b = Button(parent=camera.ui, icon='assets\settings.png', color=color.black, scale=0.09, x=-0.84, y=0.45)
# if b.on_click:
#     wp.enabled = True




#Функции для биндов
# Разблокировка мыши по нажатию клавиши:
def mouselocker(key):
    if key == 'left alt':
        mouse.locked = not mouse.locked
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
    #switch_camera(key)


app.run() #Старт игры