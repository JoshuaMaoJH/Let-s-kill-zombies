from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from ursina.audio import Audio
from ursina.text import Text
from particleSystem import Particle
import random as rd

app = Ursina()

player = FirstPersonController(collider='box')
player.gravity = 0
player.x = 1

gunData = {'level1': {'model': load_model('gun.glb'), 'damage': 1, 'scale': 1.75, 'position': (-0.15,-0.4,0), 'rotation': (0,-110,-20)},
           'level2': {'model': load_model('gun2.glb'), 'damage': 2, 'scale': 1.25, 'position': (-0.2,-0.45,0), 'rotation': (0,-110,-20)},
           'level3': {'model': load_model('gun3.glb'), 'damage': 3, 'scale': 1, 'position': (-0.6,-0.35,0), 'rotation': (0,-100,-20)}}

gunIndexDict = {'level1': 'gun1', 'level2': 'gun2', 'level3': 'gun3'}

gunLevel = 'level1'

gun = Entity(model=gunData[gunLevel]['model'],
             collider='box', parent=camera.ui,
             scale=gunData[gunLevel]['scale'],
             position=gunData[gunLevel]['position'],
             rotation=gunData[gunLevel]['rotation'])
gun.damage = gunData[gunLevel]['damage']

window.fullscreen = True
window.exit_button.visible = False
window.color = color.rgb(0,0,0)
window.fps_counter.visible = False

zombies = []
zombiesGPS = []
haveGuns = ['level1']

scene.fog_color = color.black
scene.fog_density = 0.15

player.health = HealthBar(bar_color=color.green,roundness=0,color=color.red)
player.bullet = HealthBar(bar_color=color.yellow,roundness=0,y=0.4,color=color.red)
player.bullet.text_color = player.health.text_color = color.black

terrianWidth = 150

terrainFromHeightmapTexture = Entity(model=Terrain('heightmap_1', skip=8),
                                     scale=(40, 5, 20),
                                     texture='heightmap_1')
terrainFromHeightmapTexture.visible = False

hv = terrainFromHeightmapTexture.model.height_values.tolist()

terrainFromList = Entity(model=Terrain(height_values=hv),
                         scale=(terrianWidth, 10, terrianWidth),
                         texture='heightmap_1',
                         collider='box')

GPS = Entity(model='cube', color=color.blue, scale=(0.3, 0.3), origin=(-1.985,-1.118))
GPS.parent = camera.ui

GPSplayer = Entity(model='cube', color=color.green, scale=(0.01, 0.01))
GPSplayer.posMultiply = 30
GPSplayer.origin = GPS.origin * GPSplayer.posMultiply
GPSplayer.zonePosition = (0, 0)
GPSplayer.parent = camera.ui

ouchAudio = Audio('ouch.wav', autoplay=False, loop=False)
shootingAudio = Audio('shooting1.wav', autoplay=False, loop=True)
reloadAudio = Audio('reload.wav', autoplay=False, loop=False)
zombieAudio = Audio('zombie1.wav', autoplay=False, loop=True)
bgMusic = Audio('bgMusic.wav', autoplay=True, loop=True)
bulletEmptyAudio = Audio('bulletEmpty.wav', autoplay=False, loop=True)
bulletShellAudio = Audio('bulletShell.wav', autoplay=False, loop=False)
explodeAudio = Audio('explode.wav', autoplay=False, loop=False)
bgMusic.volume = 0.5
bgMusic.play()
zombieAudio.volume = 0.1
zombieAudio.play()

bulletShellAudio_playState = 0

shootState = 0
shootAmount = 0
shootTime = 0

bulletShell_Mod = load_model('bulletShell.glb')

defeatZombieAmount = 0
updateGunDefeat = 0

generateZombieIntervalTime = 20
generateZombieAmount = 3
generateZombieTime = 0

grenadeAmount = 1

gameState = 0

score = 0

playTime = 0

MAX_THROW_POWER = 17
MIN_THROW_POWER = 5
throwPower = 10

gunText = Text(text=f'Using Gun: {gunIndexDict[gunLevel]}', origin=(0, -15), color=color.orange)
grenadeAmountText = Text(text=f'Grenade Amount: {grenadeAmount}', origin=(0, -19), color=color.orange)
scoreText = Text(text=f'Score: {score}', origin=(0,-17), color=color.orange)
timeText = Text(text=f'Play Time: {playTime}', origin=(0, -13), color=color.orange)
throwPowerText = Text(text=f'Throw Power: {throwPower}', origin=(0, -11), color=color.orange)

player.enabled = False

Text.default_font = "D:\Python\pythonProject\pythonProject-Let's kill zombies\simkai.ttf"

explodeSmokes = {}

explodeHurtDelayState = 0
explodeHurtDelay = 0

openPromptPromptText = Text(text='按shift + P打开提示', origin=(2, 15), color=color.orange)
openPromptPromptText.visible = False

reloadPromptText = Text(text='弹药不足，请按R键花费2分装填子弹', origin=(0, 2), color=color.orange)
reloadPromptText.visible = False

StartText = Text(text="在不久的将来,一种可怕的病毒肆虐地球,导致大批人类变异为嗜血丧尸。\n为拯救人类文明,全球科学家建立了一个太空殖民计划,\n在遥远的新星球“新地球”上建立人类第二家园。主人公杰克是殖民地的一名建筑工人。\n他和AI女友丽萨过着幸福生活,直到一天,殖民地的防护网挡不住大批丧尸入侵。\n原来是运送物资的宇宙飞船泄漏了病毒!杰克为保卫殖民地踏上了战斗之路。\n在绝望与战斗中,杰克成长为一名英雄式的人物。\n他不仅拯救了殖民地,还和丽萨成家,并且他们的后人世代守护和平。\n直到有一天,新的威胁来袭,杰克的后代将再次捍卫人类的家园......", origin=(0,-0.5), color=color.orange)

StartPromptText = Text(text='按空格键开始游戏', origin=(0,3), color=color.orange, scale=2)

variate1 = 5

walls = []

def hurt(entity):
    for zombie in zombies:
        if distance(entity, zombie) <= 5:
            zombie.health = 0
        elif distance(entity, zombie) <= 6:
            zombie.health = 3

    for wall in walls:
        try:
            if distance(entity, wall) <= 3:
                destroy(wall)
                walls.remove(wall)
        except Exception:
            pass

    if distance(entity, player) <= 5:
        player.health.value -= 20
        ouchAudio.play()
    elif distance(entity, player) <= 6:
        player.health.value -= 10
        ouchAudio.play()

def getY(playerOrEntity):
    return terraincast(playerOrEntity.world_position, terrainFromList, hv)

def generateWall():
    for i in range(-int(terrianWidth/2),int(terrianWidth/2)):
        for j in range(-int(terrianWidth/2),int(terrianWidth/2)):
            try:
                if hv[i][j] % 20 == 0 and hv[i][j] != 0:
                    wall = Entity(model='cube', texture='brick', scale=(1, 7, 1), position=(i, 0, j), collider='box', texture_scale=(1, 7, 1))
                    wall.y = floor(getY(wall)+1.25)
                    walls.append(wall)
            except Exception:
                pass

generateWall()

def input(key):
    global throwPower,gunLevel, shootState, shootAmount, shootTime, score, gameState,grenadeAmount
    if key == 'space' and not player.health.value <= 0:
        StartText.visible = False
        StartPromptText.visible = False
        openPromptPromptText.visible = True
        player.enabled = True
        gun.enabled = True
        gameState = 1
        try:
            a.visible = False
            b.visible = False
            c.visible = False
            d.visible = False
        except Exception:
            pass

    if key == 'escape':
        quit()

    if gameState == 1:
        if held_keys['shift'] and held_keys['p']:
            gamePrompt()

        if key == 'scroll up':
            if throwPower < MAX_THROW_POWER:
                throwPower += 1
        elif key == 'scroll down':
            if throwPower > MIN_THROW_POWER:
                throwPower -= 1

        if key == 'left mouse down':
            if player.bullet.value > 0:
                shootingAudio.play()
                shootState = 1

            if player.bullet.value <= 0:
                bulletEmptyAudio.play()

        if key == 'left mouse up':
            shootingAudio.stop()
            shootState = 0

            if player.bullet.value > 0:
                bulletShellAudio.play()

            if player.bullet.value <= 0:
                bulletEmptyAudio.stop()
                reloadPromptText.visible = False

        if key == 'r' and score >= 2:
            player.bullet.value = 100
            reloadAudio.play()
            score -= 2

        try:
            k = f'level{key}'
            if k in haveGuns:
                gun.model = gunData[k]['model']
                gun.damage = gunData[k]['damage']
                gun.scale = gunData[k]['scale']
                gun.position = gunData[k]['position']
                gun.rotation = gunData[k]['rotation']
            else:
                if k == 'level2':
                    if score >= 50:
                        gunLevel = k
                        gun.model = gunData[k]['model']
                        gun.damage = gunData[k]['damage']
                        gun.scale = gunData[k]['scale']
                        gun.position = gunData[k]['position']
                        gun.rotation = gunData[k]['rotation']
                        score -= 50
                        haveGuns.append(k)
                elif k == 'level3':
                    if score >= 70:
                        gun.model = gunData[k]['model']
                        gun.damage = gunData[k]['damage']
                        gun.scale = gunData[k]['scale']
                        gun.position = gunData[k]['position']
                        gun.rotation = gunData[k]['rotation']
                        score -= 70
                        haveGuns.append(k)
        except Exception:
            pass

        if key == 'g':
            if score >= 70:
                grenadeAmount += 1
                score -= 70

        if key == 't':
            if grenadeAmount > 0:
                grenade = Grenade(zombie_list=zombies, model='bomb.glb', collider='box', position=player.camera_pivot.world_position)
                grenade.throw(rotation=player.camera_pivot.world_rotation, power=throwPower)
                grenadeAmount -= 1

def gamePrompt():
    global gameState,a,b,c,d
    gameState = 0
    openPromptPromptText.visible = False
    player.enabled = False
    gun.enabled = False
    a = Text(text='游戏提示', origin=(0, -2), scale=3, color=color.orange)
    b = Text(text='            游戏操作：\nWASD移动\nWASD + Alt跑步\n鼠标控制视角\n左键射击\nR键装填子弹\n123键换枪，游戏开始时只拥有1号枪，可购买枪\n鼠标滚轮调整投掷力度\nG键购买手雷\nT键扔手雷\nescape键退出游戏', position=(-0.5, 0.05), scale=1.5, color=color.orange)
    c = Text(text='游戏购买/装填子弹价格：\n    2号枪：50分\n    3号枪：70分\n    装填子弹：2分\n    手雷：70分', position=(0, 0.05), scale=1.5, color=color.orange)
    d = Text(text='按空格键返回游戏', origin=(0, 7), color=color.orange, scale=2.25)

def setPlayerY():
    try:
        player.y = getY(player)
    except Exception:
        pass

def update():
    global explodeHurtDelayState,explodeHurtDelay,playTime,shootTime, bulletShellAudio_playState, shootAmount, shootState, score, generateZombieTime, generateZombieIntervalTime, generateZombieAmount
    if gameState == 1:
        GPSplayer.zonePosition = (player.x / variate1, player.z / variate1)
        GPSplayer.origin = GPS.origin * GPSplayer.posMultiply + GPSplayer.zonePosition + GPSplayer.scale / 2

        if held_keys['alt']:
            player.speed = 10
        else:
            player.speed = 5

        if shootState == 1 and player.bullet.value <= 0:
            shootingAudio.stop()
            shootState = 0

        if bulletShellAudio_playState == 0 and player.bullet.value <= 0:
            bulletShellAudio.play()
            bulletShellAudio_playState = 1

        if player.bullet.value > 0:
            bulletShellAudio_playState = 0

        for zombie in zombies:
            zombieDistances = []
            for zombie2 in zombies:
                zombieDistances.append(distance(zombie2, player))
            zombieDistances.sort()
            zombieAudio.volume = 1.5 / zombieDistances[0]

            try:
                zombiesGPS[zombies.index(zombie)].zonePosition = (zombie.x / variate1, zombie.z / variate1)
                zombiesGPS[zombies.index(zombie)].origin = GPS.origin * zombiesGPS[zombies.index(zombie)].posMultiply + zombiesGPS[zombies.index(zombie)].zonePosition + zombiesGPS[zombies.index(zombie)].scale / 2
            except Exception:
                pass

            if zombie.health <= 0:
                zombies.remove(zombie)
                zombiesGPS.remove(zombie.GPS)
                destroy(zombie)
                destroy(zombie.GPS)
                score += 5

        generateZombieTime += time.dt

        if len(zombies) == 0:
            zombieAudio.volume = 0

        if generateZombieTime >= generateZombieIntervalTime:
            for i in range(generateZombieAmount):
                generateZombie()
                generateZombieIntervalTime = random.uniform(5, 20)
                generateZombieAmount = random.randint(3, 10)
                generateZombieTime = 0

        if player.health.value <= 0:
            gameOver()

        updateTextContent()

        if explodeHurtDelayState == 1:
            explodeHurtDelay += time.dt
            if distance(explodeSmokes[len(explodeSmokes) - 1][0], player) <= 5:
                hurt(explodeSmokes[len(explodeSmokes) - 1][0])
                explodeHurtDelay = 0
                explodeHurtDelayState = 0
                explodeSmokes.pop(len(explodeSmokes) - 1)
            else:
                if explodeHurtDelay >= 0.7:
                    hurt(explodeSmokes[len(explodeSmokes) - 1][0])
                    explodeHurtDelay = 0
                    explodeHurtDelayState = 0
                    explodeSmokes.pop(len(explodeSmokes) - 1)

        if held_keys['left mouse']:
            if player.bullet.value <= 0:
                reloadPromptText.visible = True

        if shootState == 1 and player.bullet.value > 0:
            shootTime += time.dt
            if shootTime >= 0.078:
                shootAmount += 1
                player.bullet.value -= 1
                gun.shake(duration=0.1, magnitude=0.05)
                if gunLevel == 'level1':
                    bulletShell = Entity(model=bulletShell_Mod, collider='box', scale=0.2, parent=camera.ui, position=(0.3,-0.3,0), rotation=(0,-110,65))
                elif gunLevel == 'level2':
                    bulletShell = Entity(model=bulletShell_Mod, collider='box', scale=0.2, parent=camera.ui, position=(0.4,-0.3,0), rotation=(0,-110,65))
                elif gunLevel == 'level3':
                    bulletShell = Entity(model=bulletShell_Mod, collider='box', scale=0.2, parent=camera.ui, position=(0.2,-0.3,0), rotation=(0,-110,65))

                bulletShell.animate_position(bulletShell.position - (bulletShell.forward * 0.2), curve=curve.linear, duration=0.1)
                destroy(bulletShell, delay=0.1)
                e = mouse.hovered_entity
                if e in zombies:
                    e.health -= gun.damage
                    e.blink(color.red, duration=0.1)
                    for i in range(5):
                        Particle(position=e.world_position + (0, 1, 0), particleScale=0.05, range=0.12)

                shootTime = 0

        playTime += time.dt

        setPlayerY()

        playTimeUpdateNum = str(playTime).split('.')
        playTimeUpdateNum1 = playTimeUpdateNum[0]
        playTimeUpdateNum2 = playTimeUpdateNum[1][0:2]
        playTime = float(f'{playTimeUpdateNum1}.{playTimeUpdateNum2}')

def normalize(vec):
    length = vec.length()
    if length > 0:
        return vec / length
    else:
        return vec

def generateZombie():
    zombie = Zombie(zombie_list=zombies, model=load_model('zombie.obj'), collider='box', texture=load_texture('zombie.png'), camera=camera)
    terrianWidthHalf = terrianWidth / 2
    zombiePosXRandom = random.uniform(-terrianWidthHalf, terrianWidthHalf)
    zombiePosZRandom = random.uniform(-terrianWidthHalf, terrianWidthHalf)
    zombie.position = (zombiePosXRandom, 0, zombiePosZRandom)
    zombie.GPS = Entity(model='cube', color=color.red, scale=(0.01, 0.01))
    zombie.GPS.posMultiply = 30
    zombie.GPS.origin = GPS.origin * GPSplayer.posMultiply
    zombie.GPS.zonePosition = (0, 0)
    zombie.GPS.parent = camera.ui
    zombiesGPS.append(zombie.GPS)
    zombies.append(zombie)

def updateTextContent():
    scoreText.text = f'Score: {score}'
    if gun.model == gunData['level1']['model']:
        gunText.text = f'Using Gun: {gunIndexDict["level1"]}'
    elif gun.model == gunData['level2']['model']:
        gunText.text = f'Using Gun: {gunIndexDict["level2"]}'
    elif gun.model == gunData['level3']['model']:
        gunText.text = f'Using Gun: {gunIndexDict["level3"]}'
    grenadeAmountText.text = f'Grenade Amount: {grenadeAmount}'
    timeText.text = f'Play Time: {playTime}'
    throwPowerText.text = f'Throw Power: {throwPower}'
    player.health.text = f'Health: {player.health.value}/100'
    player.bullet.text = f'Bullets: {player.bullet.value}/100'
    if player.health.value < 40:
        player.health.bar_color = color.orange
    elif player.health.value < 70:
        player.health.bar_color = color.yellow
    else:
        player.health.bar_color = color.green

    if player.bullet.value < 40:
        player.bullet.bar_color = color.orange
    elif player.bullet.value < 70:
        player.bullet.bar_color = color.yellow
    else:
        player.bullet.bar_color = color.green

updateTextContent()

def gameOver():
    global gameState
    player.enabled = False
    gun.enabled = False
    scoreText.visible = False
    gunText.visible = False
    grenadeAmountText.visible = False
    timeText.visible = False
    throwPowerText.visible = False
    player.health.visible = False
    player.bullet.visible = False
    grenadeAmountText.visible = False
    openPromptPromptText.visible = False
    gameState = 0
    shootingAudio.stop()
    Text(text=f'Score: {score}', scale=3, origin=(0,3.5), color=color.white)
    Text(text=f'Level: {int(playTime/100)+int(score/100)}', scale=3, origin=(0,5), color=color.white)
    Text(text=f'Play Time: {playTime}', scale=3, origin=(0,2), color=color.white)
    Text(text='Game Over', scale=10, origin=(0,0), color=color.white)

class Grenade(Entity):
    def __init__(self, zombie_list, **kwargs):
        super().__init__(**kwargs)
        self.throwState = 0
        self.gravity = 9.8
        self.vy = 0
        self.power = 0
        self.fallDelayTime = 0
        self.fallDelay = 0
        self.zombieList = zombie_list

    def throw(self, rotation, power):
        self.power = power / 2
        self.rotation = rotation
        self.fallDelayTime = power / 25
        self.throwState = 1

    def update(self):
        if self.throwState == 1:
            self.position += self.forward * self.power * time.dt
            self.fallDelay += time.dt
            if self.fallDelay > self.fallDelayTime:
                self.vy += 3 * time.dt
                self.y -= self.vy * time.dt

            try:
                if self.y <= terraincast(self.position, terrainFromList, hv) - 1:
                    self.explode()
                for zombie in self.zombieList:
                    if distance(self, zombie) <= 1.15:
                        self.explode()

                for wall in walls:
                    if distance(self, wall) <= 1.15:
                        self.explode()
            except Exception:
                pass

    def explode(self):
        global explodeHurtDelayState
        self.variate1 = self.position
        explodeSmoke = Entity(model='sphere', scale=1, position=self.variate1, color=color.rgb(255, 0, 0, 230))
        explodeSmoke2 = Entity(model='sphere', scale=1, position=self.variate1, color=color.rgb(255, 210, 210, 170))

        explodeSmoke.animate_scale((10, 10, 10), curve=curve.linear, duration=1)
        explodeSmoke2.animate_scale((12, 12, 12), curve=curve.linear, duration=1)

        explodeSmoke.animate_color(color.rgb(255, 255, 255, 0), curve=curve.linear, duration=1)
        explodeSmoke2.animate_color(color.rgb(255, 255, 255, 0), curve=curve.linear, duration=1)

        explodeSmokes[len(explodeSmokes)] = [explodeSmoke,explodeSmoke2]

        explodeAudio.volume = 2 / distance(explodeSmoke, player)
        explodeAudio.play()

        destroy(explodeSmoke, delay=1)
        destroy(explodeSmoke2, delay=1)

        for i in range(50):
            Particle(position=self.variate1, particleScale=0.05, range=0.3, speed=10)

        explodeHurtDelayState = 1

        player.camera_pivot.shake(duration=1.5)

        destroy(self)

class Zombie(Entity):
    def __init__(self, zombie_list, **kwargs):
        super().__init__(**kwargs)
        self.health = 10
        self.speed = random.uniform(0.5, 2)
        self.damage = 3
        self.update_intervalDamage = 3
        self.damageAmount = 0
        self.damageIntervalState = 0
        self.damageInterval = 0
        self.damageIntervalTime = 2
        self.target = player
        self.targetDistance = 0
        self.zombieList = zombie_list
        self.state = 'walk'

    def update(self):
        self.targetDistance = distance(self, self.target)
        self.look_at(self.target, axis='forward')
        self.rotation_x = self.rotation_z = 0
        self.rotation_y += 180

        self.avoidZombies()
        self.avoidWalls()

        if self.targetDistance > 1.4:
            self.state = 'walk'
            direction = self.target.position - self.position
            direction.normalized()
            self.position += direction * 0.5 * time.dt

        if self.targetDistance < 1.5 and self.damageIntervalState == 0:
            self.state = 'attack'
            self.target.health.value -= self.damage
            ouchAudio.play()
            self.damageAmount += 1
            self.damageIntervalState = 1

        if self.damageAmount >= self.update_intervalDamage:
            self.damageAmount = 0
            self.update_intervalDamage += 1
            self.speed += 1
            self.damage += 2
            self.health += 2
            self.blink(color.yellow, duration=0.5)

        if self.damageIntervalState == 1:
            self.state = 'idle'
            self.damageInterval += time.dt
            if self.damageInterval >= self.damageIntervalTime:
                self.damageInterval = 0
                self.damageIntervalState = 0

        try:
            self.y = getY(self)
        except Exception:
            pass

    def avoidZombies(self):
        self.nearestX = min([distance(self, x) for x in self.zombieList if x != self], default=0)
        self.nearestZ = min([distance(self, z) for z in self.zombieList if z != self], default=0)
        try:
            if self.nearestX < 1.15:
                nearestZombie = self.getNearestZombie()
                avoidDir = normalize(self.position - nearestZombie.position)
                self.position += avoidDir * self.speed * time.dt

            if self.nearestZ < 1.15:
                nearestZombie = self.getNearestZombie()
                avoidDir = normalize(self.position - nearestZombie.position)
                self.position += avoidDir * self.speed * time.dt
        except Exception:
            pass

    def getNearestZombie(self):
        try:
            distances = [distance(self, z) for z in self.zombieList if z != self]
            distances.sort()
            nearestZombie = self.zombieList[distances.index(distances[0])]
            return nearestZombie
        except Exception:
            return None

    def avoidWalls(self):
        self.nearestX2 = min([distance(self, x) for x in walls], default=0)
        self.nearestZ2 = min([distance(self, z) for z in walls], default=0)
        try:
            if self.nearestX2 < 1.7:
                nearestWall = self.getNearestWall()
                avoidDir = normalize(self.position - nearestWall.position)
                self.position += avoidDir * self.speed * time.dt

            if self.nearestZ2 < 1.7:
                nearestWall = self.getNearestWall()
                avoidDir = normalize(self.position - nearestWall.position)
                self.position += avoidDir * self.speed * time.dt
        except Exception:
            pass

    def getNearestWall(self):
        try:
            distances = [distance(self, w) for w in walls]
            distances.sort()
            nearestWall = walls[distances.index(distances[0])]
            return nearestWall
        except Exception:
            return None

app.run()