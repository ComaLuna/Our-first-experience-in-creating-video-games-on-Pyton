from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

#Окно игры:
app = Ursina(
    title='Name',
    fps_counter=False,
    vsync=True,
    entity_counter=False,

)
#Переменые: (их пока нет)

#Модельки мира
sky = Sky()
ground = Entity(model='plane', collider='box', scale=640, texture='grass', texture_scale=(30,30))

#Бинды (они пока выключены)
# def Update():

#зрение от первого лица и игрок:
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-10, color=color.blue, origin_y=-0.5, speed=8, collider='box')
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

#Ui настроек (пока не работает)
b = Button(parent=camera.ui, icon='assets\settings.png', color=color.black, scale=0.09, x=-0.84, y=0.45)


app.run() #Старт игры