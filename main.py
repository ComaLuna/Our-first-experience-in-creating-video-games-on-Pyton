from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader


#Окно игры:
app = Ursina(
    title='Name',
    fps_counter=False,
    vsync=True,
    entity_counter=False,
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

#Бинды
# Разблокировка мыши по нажатию клавиши:
def input(key):
    if key == 'left alt':
        mouse.locked = not mouse.locked

#Это в разработке
# def switch_camera(key):
#     global camera_mode
#     if held_keys['z']:
#         if camera_mode == 'first_person':
#             EditorCamera(enabled=False)
#             camera_mode = 'third_person'
#         else: #Переключение на вид от первого лица
#             EditorCamera(enabled=True)
#             camera_mode = 'first_person'

app.run() #Старт игры