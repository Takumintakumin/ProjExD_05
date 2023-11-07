import math
import random
import sys
import time

import pygame as pg
from pygame.sprite import AbstractGroup


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ


def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：飛行機のSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクターに関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    
    def __init__(self, num: int, xy: tuple[int, int]):
        """
        飛行機画像Surfaceを生成する
        引数1 num：飛行機画像ファイル名の番号
        引数2 xy：飛行機画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex05/w.png"), 0, 0.2)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.dire = (+1, 0)
        self.state = "normal"
        self.hyper_life = 1

    
    def change_img(self, num: int, screen: pg.Surface):
        """
        飛行機画像を切り替え，画面に転送する
        引数1 num：飛行機画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/w.png"), 0, 0.2)
        screen.blit(self.image, self.rect)

    
    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じて飛行機を移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        if self.state == "hyper":
            self.hyper_life -= 1
            self.image = pg.transform.rotozoom(pg.image.load("ex05/barrier.png"), 0, 0.4)
        if self.state == "hyper" and self.hyper_life <0:
            self.change_state("normal", -1)
         
        screen.blit(self.image, self.rect)
    
    
    def get_direction(self) -> tuple[int, int]:
        return self.dire
    
    
    def change_state(self, state, hyper_life):
        self.state = state
        self.hyper_life = hyper_life

class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class BossBomb(pg.sprite.Sprite):
    """
    ボスの爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, boss: "Boss", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 boss：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(50, 80)  # 爆弾円の半径：80以上100以下の乱数
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        self.image = pg.Surface((2.5*rad, 2.5*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(boss.rect, bird.rect)  
        self.rect.centerx = boss.rect.centerx
        self.rect.centery = boss.rect.centery+boss.rect.height/2
        self.speed = 9

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.get_direction()
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load(f"ex04/fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10


    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Boss", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load("ex04/fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life


    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"ex04/fig/alien{i}.png") for i in range(1, 4)]
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, HEIGHT/2)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル


    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy

class Boss(pg.sprite.Sprite):
    """
    ボスに関するクラス
    """
    imgs = [pg.image.load("ex05/shinigami.png")]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(1000, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, HEIGHT/2)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        """
        bossを速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy


class Boss_hp(): 
    """
    ボスのヒットポイントに関するクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.boss_hp = 10
        self.image = self.font.render(f"Boss_hp: {self.boss_hp}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 1000, HEIGHT-50 
    
    def hp_down(self,down):
        self.boss_hp -= down

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Boss_hp: {self.boss_hp}", 0, self.color)
        screen.blit(self.image, self.rect)



class Zanki:
    """
    自分の残機を表示するクラス
    初期残機 3
    回復 1
    """

    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (255, 255, 255)
        self.zanki = 3
        self.zimage = self.font.render(f"HP: {self.zanki}", 0, self.color)
        self.rect  =self.zimage.get_rect()
        self.rect.center = 100, HEIGHT-90


    def zanki_up(self,add):
        self.zanki += add
    

    def zanki_down(self, down):
        self.zanki -= down


    def update(self, screen: pg.Surface):
        self.zimage = self.font.render(f"HP: {self.zanki}", 0 , self.color)
        screen.blit(self.zimage, self.rect) 


class gameover:
    """
    ゲームオーバー時の表示するクラス
    """
    def __init__(self):
        self.font  =pg.font.Font(None, 50)
        self.color = (255, 255, 255)
        self.image = self.font.render("Game Over", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 750,HEIGHT -450
    
    def update(self, screen: pg.Surface):
        self.gimage = self.font.render(f"Game Over", 0 , self.color)
        screen.blit(self.gimage, self.rect)

class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (255, 255, 255)
        self.score = 0
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def score_up(self, add):
        self.score += add
    

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.image, self.rect)


def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("ex05/Uchu.jpg") #宇宙背景
    clock  = pg.time.Clock()
    bg_img2 = pg.transform.flip(bg_img, True, False)
    score = Score()
    boss_hp = Boss_hp()
    zanki = Zanki()
    go = gameover()
    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    bosses = pg.sprite.Group()
    bossbombs = pg.sprite.Group()

    tmr = 0
    clock =  pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.add(Beam(bird))
        screen.blit(bg_img, [0, 0])

        if tmr%200 == 0 and bosses is not None:
            if len(bosses) < 1:  # 200フレームに1回，敵機を出現させる
                emys.add(Enemy())
        #if tmr%400 == 0:
         #   bosses.add(Boss())
        if score.score >= 10 and bosses is not None:
                if len(bosses) < 1:
                    
                    bosses.add(Boss())

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bomb(emy, bird))
        
        for boss in bosses:
            if boss.state == "stop" and tmr%5 == 0:
                bombs.add(BossBomb(boss,bird))
                
            #elif bomb_count % 10 == 0:


        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.score_up(10)  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
        
        for boss in pg.sprite.groupcollide(bosses, beams, True, True).keys():
            boss_hp.hp_down(int(1))
            if boss_hp.boss_hp == 0:
                exps.add(Explosion(boss, 400))  # 爆発エフェクト
                score.score_up(100)  # 10点アップ
            

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.score_up(1)  # 1点アップ

        for bossbomb in pg.sprite.groupcollide(bossbombs,beams,True,True).keys():
            exps.add(Explosion(bossbomb,400))
            score.score_up(3)

        for bomb in pg.sprite.spritecollide(bird, bombs, True):
            if bird.state == "normal":
                zanki.zanki_down(1) # 残機１なくなる
                bird.change_state("hyper", 100)
                if(zanki.zanki == 0):
                    go.update(screen)  #ゲームオーバー表示
                    score.update(screen)
                    zanki.update(screen)
                    pg.display.update()
                    time.sleep(2)
                    return
            if bird.state == "hyper":
                exps.add(Explosion(bomb, 50))  
        
        x = tmr%6400
        screen.blit(bg_img, [-x, 0])
        screen.blit(bg_img2, [1600-x, 0])
        screen.blit(bg_img, [3200-x, 0])
        screen.blit(bg_img2, [4800-x, 0])
        screen.blit(bg_img, [6400-x, 0])
        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        bosses.update()
        bosses.draw(screen)
        bombs.update()
        bombs.draw(screen)
        bossbombs.update()
        bossbombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        boss_hp.update(screen)
        zanki.update(screen)    
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
