import sys
from gc import enable
from sys import orig_argv
from PIL.DdsImagePlugin import module
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader, transition_shader
from numpy import floor
from perlin_noise import PerlinNoise #Шум перлина дужен для генерации(ОН НЕ БЕСПОЛЕЗЕН)
import time
from random import randint

#Окно игры:
app = Ursina(
    title='Name',
    fps_counter=False,
    vsync=True,
    entity_counter=False,
    development_mode=False,
    icon='assets/Myfirstgame.ico'
)

#Модельки мира
scene.Shader = lit_with_shadows_shader
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 0))
sky = Sky()
scene.fog_color = color.rgb(150,150,200)
def fogScattering():
    if player.speed > 10:
        scene.fog_density = lerp(scene.fog_density, 0.07, time.dt)
    else:
        scene.fog_density = lerp(scene.fog_density, 0.04, time.dt)


#зрение от первого лица и игрок:
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', color=color.cyan, origin_y=-0.5, speed=8, collider='box',
                               gravity = 0.8, jump_up_duration = 0.75)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

#Ui настроек
def ExitButton():
    sys.exit()

def toggleSettingPanel():
    settings_panel.enabled = not settings_panel.enabled

def toggle_fullscreen():
    if FullScreenMode.value > 0.5:
        window.fullscreen = True
    else:
        window.fullscreen = False

def set_fps(value):
    application.target_fps = int(value)

def create_settings_panel():
    def apply_settings():
        settings_panel.enabled = False

    settings_panel = WindowPanel(title="Settings", content=(
        Text("Full screen:"),
        Slider(min=0, max=1, step=1, default=1, color=color.azure, dynamic=False),
        Text("Target FPS:"),
        Slider(min=30, max=240, step=30, default=60, color=color.azure, dynamic=False),
        Button(text="Close menu", color=color.dark_gray, on_click=apply_settings),
        Button(text="Exit", color=color.red, on_click=ExitButton),
    ), position=(0, 0))
    FullScreenMode = settings_panel.content[1]
    FPSSlider = settings_panel.content[3]
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

b = Button(parent=camera.ui, icon='assets\settings.png', color=color.black, scale=0.056, x=-0.86, y=0.47)
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
sand_texture = load_texture("assets/textures/sand.png")
dirt_texture = load_texture("assets/textures/dirt.png")
log_texture = load_texture("assets/textures/Tree/log.png")
leaf_texture = load_texture("assets/textures/Tree/img.png")


class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            model='cube',
            texture=texture,
            position=position,
            origin_y=0.5,
            scale=1,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            # highlight_color=color.lime,
            # shader=lit_with_shadows_shader
        )
    #     self.health = 10  # Количество ударов для разрушения
    #     self.max_health = 10
    #     self.break_stage = 0  # Текущая стадия разрушения (0-4)
    #     self.break_effect = None  # Эффект трещин
    #     self.texture.filtering = None
    #
    # def damage(self):
    #     if self.health <= 0:
    #         return
    #
    #     self.health -= 1
    #     self.hit_sound.play()
    #
    #     # Обновляем стадию разрушения (0-4)
    #     self.break_stage = 4 - int((self.health / self.max_health) * 4)
    #     self.update_break_effect()
    #
    #     if self.health <= 0:
    #         self.destroy()
    #
    # def update_break_effect(self):
    #     if self.break_stage > 0:
    #         if not self.break_effect:
    #             self.break_effect = Entity(
    #                 parent=self,
    #                 model='cube',
    #                 texture='assets/textures/cracks.png',
    #                 scale=1.01,
    #                 double_sided=True,
    #                 transparent=True
    #             )
    #         # Меняем UV текстуры для разных стадий
    #         self.break_effect.texture_offset = (0, (4 - self.break_stage) * 0.25)
    #     elif self.break_effect:
    #         destroy(self.break_effect)
    #         self.break_effect = None
    #
    # def destroy(self):
    #     # Эффект разрушения
    #     self.break_sound.play()
    #     for i in range(8):  # Частицы
    #         particle = Entity(
    #             model='cube',
    #             texture=self.texture,
    #             position=self.position,
    #             scale=0.2,
    #             lifespan=0.8
    #         )
    #         particle.animate_position(
    #             particle.position + Vec3(random.uniform(-1, 1), random.uniform(-0.5, 1), random.uniform(-1, 1)),
    #             duration=0.8
    #         )
    #         particle.animate_scale(0, duration=0.8)
    #
    #     # Удаляем блок из мира
    #     block_pos = (int(self.x), int(self.y), int(self.z))
    #     if block_pos in blocks:
    #         del blocks[block_pos]
    #     destroy(self)
# Класс для деревьев
class Tree:
    def __init__(self, position):
        x, y, z = position
        # Ствол дерева (3 блока в высоту)
        for i in range(3):
            block_pos = (x, y + i + 1, z)
            blocks[block_pos] = Voxel(position=block_pos, texture=log_texture)

        # Листья (простая крона)
        leaf_positions = [
            (x, y + 4, z),  # центр
            (x + 1, y + 4, z), (x - 1, y + 4, z), (x, y + 4, z + 1), (x, y + 4, z - 1),  # крест
            (x, y + 5, z)  # верх
        ]

        for pos in leaf_positions:
            blocks[pos] = Voxel(position=pos, texture=leaf_texture)


#Генерация Мира
# Настройки генерации мира
CHUNK_SIZE = 1  # Размер чанка
RENDER_DISTANCE = 10  # В чанках
loaded_chunks = {}  # Словарь для хранения загруженных чанков
blocks = {}  # Словарь для хранения всех блоков

# Генерация мира
noise = PerlinNoise(octaves=2, seed=randint(1, 10000))
biome_noise = PerlinNoise(octaves=1, seed=randint(1, 10000))
tree_noise = PerlinNoise(octaves=3, seed=randint(1, 10000))
amp = 6
freq = 24
BIOME_SCALE = 10000
DESERT_THRESHOLD = 0.000001

def get_chunk_key(position):
    x = floor(position[0] / CHUNK_SIZE)
    z = floor(position[2] / CHUNK_SIZE)
    return (x, z)


def generate_chunk(chunk_x, chunk_z):
    chunk_key = (chunk_x, chunk_z)
    if chunk_key in loaded_chunks:
        return

    loaded_chunks[chunk_key] = True

    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            world_x = x + chunk_x * CHUNK_SIZE
            world_z = z + chunk_z * CHUNK_SIZE

            # Определяем биом (пустыня или обычная местность)
            biome_value = biome_noise([world_x / BIOME_SCALE, world_z / BIOME_SCALE])
            is_desert = biome_value > DESERT_THRESHOLD

            # Генерация высоты
            y = floor(noise([world_x / freq, world_z / freq]) * amp)

            # Основной блок (трава или песок)
            block_pos = (world_x, y, world_z)
            blocks[block_pos] = Voxel(
                position=block_pos,
                texture=sand_texture if is_desert else grass_texture
            )

            # 3 слоя грязи под землей
            for i in range(1, 4):
                dirt_pos = (world_x, y - i, world_z)
                blocks[dirt_pos] = Voxel(position=dirt_pos, texture=dirt_texture)

            # Генерация деревьев (только не в пустыне)
            if not is_desert and tree_noise([world_x / 10, world_z / 10]) > 0.5:
                Tree((world_x, y, world_z))

def delete_far_chunks():
    player_chunk = get_chunk_key(player.position)
    chunks_to_remove = []
    for chunk_key in loaded_chunks.keys():
        dist = max(abs(chunk_key[0] - player_chunk[0]), abs(chunk_key[1] - player_chunk[1]))
        if dist > RENDER_DISTANCE:
            chunks_to_remove.append(chunk_key)
    for chunk_key in chunks_to_remove:
        remove_chunk(chunk_key)

def remove_chunk(chunk_key):
    if chunk_key in loaded_chunks:
        del loaded_chunks[chunk_key]
        chunk_x, chunk_z = chunk_key

        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                world_x = x + chunk_x * CHUNK_SIZE
                world_z = z + chunk_z * CHUNK_SIZE

                # Удаляем все блоки в этой колонке
                for y in range(20, -20, -1):
                    block_pos = (world_x, y, world_z)
                    if block_pos in blocks:
                        destroy(blocks[block_pos])
                        del blocks[block_pos]

def update_chunks():
    player_chunk = get_chunk_key(player.position)

    for x in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
        for z in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            chunk_x = player_chunk[0] + x
            chunk_z = player_chunk[1] + z
            generate_chunk(chunk_x, chunk_z)

    delete_far_chunks()

# Генерируем начальные чанки
for x in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
    for z in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
        generate_chunk(x, z)

class LifespanEntity(Entity):
    def __init__(self, lifespan=1, **kwargs):
        super().__init__(**kwargs)
        self.lifespan = lifespan
        invoke(destroy, self, delay=lifespan)

Entity.lifespan = None
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



#ХЕЛБАР
# Хелбар (индикатор здоровья) в левом нижнем углу
health_bar = Entity(
    parent=camera.ui,  # UI-слой
    model="quad",
    color=color.green,
    scale=(0.5, 0.035),  # Размер
    position=(-0.85, -0.45),  # Перемещаем в левый нижний угол
    origin=(-0.5, 0)  # Точка отсчета слева
)

# Переменные для отслеживания урона и регенерации
health = 100.0  # Текущее здоровье (от 0 до 1)
last_damage_time = 0  # Время последнего урона
regen_rate = 0.01  # Скорость регенерации
regen_delay = 5  # Через сколько секунд начнется регенерация
is_dead = False  # Флаг смерти игрока

def die_animation_loop():
    if death_heart.enabled:  # Проверяем, что  игрок все еще мертв
        death_heart.animate_scale(0.25, duration=0.5, curve=curve.in_out_sine)
        death_heart.animate_scale(0.2, duration=0.5, delay=0.5, curve=curve.in_out_sine)
        invoke(die_animation_loop, delay=1)
heart_sound = Audio('sounds/heartbeat.mp3', autoplay=False, loop=True)
def die():
    global Exit_on_die, Reset_on_die
    # Отключаем игрока и обычный мир
    player.enabled = False
    is_dead = True
    # Включаем эффекты смерти
    death_overlay.enabled = True
    death_heart.enabled = True
    heart_sound.play()
    # Анимация пульсации сердца
    death_heart.animate_scale(0.25, duration=0.5, curve=curve.in_out_sine)
    death_heart.animate_scale(0.2, duration=0.5, delay=0.5, curve=curve.in_out_sine)
    #озврат текстуры сердца
    death_heart.texture = 'assets/textures/heart'
    # Циклическое повторение анимации
    invoke(die_animation_loop, delay=1)
    invoke(stop_died_animation, delay=3)
    Exit_on_die = Button(text="Exit",parent=camera.ui,on_click=ExitButton, color=color.red, scale=(0.5, 0.035), x=0.0, y=-0.45)
    Reset_on_die = Button(text="Respawn", parent=camera.ui, on_click=revive, color=color.red, scale=(0.5, 0.035), x=0.0, y=-0.40)

#Анимация смерти
death_heart = Entity(
    model='quad',
    texture='assets/textures/heart.png',
    scale=1,
    parent=camera.ui,
    enabled=False# Сначала скрыто
)

# Затемнение экрана
death_overlay = Entity(
    model='quad',
    color=color.black,
    scale=(2, 2),
    parent=camera.ui,
    enabled=False
)
death_overlay.color = color.clear
death_overlay.animate_color(color.black, duration=1)

#Проверка что хп = 0 и старт анимации
def Check_health(health):
    if health <= 0 and player.enabled:
            die()
def stop_died_animation():
    death_heart.texture = 'assets/textures/break_heart'
    death_heart.animate_scale((1, 1))
    heart_sound.stop()
# Функция для нанесения урона
def take_damage(amount):
    global health, last_damage_time, is_dead

    if is_dead:  # Если игрок мертв, урон не проходит
        return

    health = max(health - amount, 0)  # Уменьшаем здоровье, но не даем уйти ниже 0
    health_bar.scale_x = max(health * 0.005, 0.001)  # Минимальный размер (чтобы не пропадал)
    last_damage_time = time.time()  # Запоминаем время последнего урона

    if health == 0:
        health_bar.color = color.red  # Если здоровье закончилось



# Если прошло 5 секунд без урона - восстанавливаем здоровье
def regen(is_dead,health):
    if not is_dead and time.time() - last_damage_time > regen_delay and health < 100.0:
        health = min(health + regen_rate, 1.0)  # Увеличиваем здоровье, но не больше 1
        health_bar.scale_x = max(health * 0.5, 0.01)  # Минимальный размер (чтобы не пропадал)

        if health > 0:
            health_bar.color = color.green  # Если началось восстановление, возвращаем цвет


# Функция для респавна (нажмите "R" для возрождения)
def taken_damage_pressing_R(key):
    global health, is_dead
    if key == "r":
        take_damage(20.0)  # Уменьшаем хелбар при нажатии пробела
        
def revive():
    global health, is_dead
    player.enabled = True
    # Отключаем эффекты смерти
    death_overlay.enabled = False
    death_heart.enabled = False

    health = 100.0  # Полностью восстанавливаем здоровье
    health_bar.scale_x = max(health * 0.005, 0.001)  # Минимальный размер (чтобы не пропадал)
    health_bar.color = color.green

    Exit_on_die.enabled = False
    Reset_on_die.enabled = False

    # Возвращаем игрока на стартовую позицию
    player.position = (0, 0, 0)
    is_dead = False
# Функции ходьбы
moving = False
walk_sound = Audio('sounds/Moving.mp3', loop=False, autoplay=False)
def def_moving():
    global moving

    # Проверяем нажатия клавиш
    if held_keys['a']:  # движение влево
        #player.x -= 5 * time.dt
        moving = True
    elif held_keys['d']:  # движение вправо
        moving = True
    elif held_keys['w']:  # движение вперёд
       moving = True
    elif held_keys['s']:  # движение назад
        moving = True
    else:
        moving = False

    # Воспроизведение звука ходьбы
def moving_sound():
    if moving and not walk_sound.playing:
        walk_sound.play()

#Бинды
def input(key):
    mouselocker(key)
    esc_Menu(key)
    taken_damage_pressing_R(key)

# Функция обновления (каждый кадр)
def update():
    global health, is_dead
    Check_health(health)
    regen(is_dead, health)
    def_moving()
    moving_sound()
    update_chunks()
    fogScattering()
app.run() #Старт игры