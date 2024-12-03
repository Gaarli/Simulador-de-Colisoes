"""
Nome do Projeto: SIMULADOR DE COLISÕES

Descrição:  O programa é um simulador de colisões bidimensional usando a biblioteca Pygame. 
            Seu objetivo principal é criar e animar um conjunto de bolas com propriedades personalizáveis, como massa, 
            velocidade e raio, que se movem dentro de uma janela, interagem entre si e com as bordas da tela, 
            obedecendo às leis de conservação de momento linear durante colisões.

Autores: 
    Matheus Araujo Pinheiro (14676810)
    Bruno Gonçalves         (14762111)
    Gabriel Araujo Lima     (14571376)
    Luis Henrique Poncianio (15577760)
    

Este projeto faz parte do processo avaliativo da disciplina 7600105 - Física Básica I (2024) da USP-São Carlos ministrada pela(o) [Prof. Krissia de Zawadzki/Esmerindo de Sousa Bernardes]
OBS: Turma do Esmerindo de Sousa Bernardes
"""



import pygame, sys
from pygame.locals import *
from random import randint

import math

# Inicialização do Pygame
pygame.init()

FPS = 60
fpsClock = pygame.time.Clock()

# Definindo os parâmetros padrões para inicialização do jogo
N = 10 # Número de bolas
V_MAX = 5  # Velocidade máxima
V_MIN = 0 # Velocidade mínima
MASS_MIN = 20  # Massa mínima das bolas
MASS_MAX = 40  # Massa máxima das bolas
RATIO = 1 # Fator de escala para o raio das bolas
WIDTH, LENGTH = 800, 480  # Dimensões da janela do jogo
window = pygame.display.set_mode((WIDTH, LENGTH), pygame.RESIZABLE)
pygame.display.set_caption("Simulador de Colisões")

# Função para gerar cores aleatórias
def gerar_cor():
    """
    Gera uma cor RGB aleatória.
    :return: Tupla representando uma cor RGB aleatória.
    """
    return (randint(0, 255), randint(0, 255), randint(0, 255))

# Classe das bolas
class Bola:
    """
    Construtor da classe Bola.
    :parâmetro screen: Superfície onde a bola será desenhada.
    """
    def __init__(self, screen):
        """
        Inicializa uma nova bola com atributos aleatórios.
        :param screen: Superfície onde a bola será desenhada.
        """
        self.screen = screen
        self.color = gerar_cor()  # A cor agora é aleatória
        self.mass = randint(MASS_MIN, MASS_MAX)
        self.radius = int(RATIO * self.mass)
        self.x = 0
        self.y = 0
        self.pos = pygame.math.Vector2(self.x, self.y)
        self.vx = randint(V_MIN, V_MAX)
        self.vy = randint(V_MIN, V_MAX)
        self.v = pygame.math.Vector2(self.vx, self.vy)
        self.trajectory = []  # Lista para armazenar a trajetória
        self.trajectory_lifetime = 100  # Quantidade de quadros para manter a trajetória

    def draw(self):
        """
        Desenha a bola na tela.
        """
        pygame.draw.circle(self.screen, self.color, self.pos, self.radius)
        
        # Desenhando a massa no centro da bola
        font = pygame.font.Font(None, 24)
        mass_text = font.render(f'{self.mass}', True, (255, 255, 255))
        self.screen.blit(mass_text, (self.pos[0] - mass_text.get_width() // 2, self.pos[1] - mass_text.get_height() // 2))
        
        # Exibindo o módulo da velocidade acima da bola
        speed = math.hypot(self.vx, self.vy)
        speed_text = font.render(f'{speed:.2f}', True, (255, 255, 255))
        self.screen.blit(speed_text, (self.pos[0] - speed_text.get_width() // 2, self.pos[1] - self.radius - 20))

    def move(self):
        """
        Atualiza a posição da bola com base em sua velocidade.
        Também registra sua trajetória.
        """
        self.pos += self.v
        self.trajectory.append(self.pos.copy())  # Adiciona a posição atual à trajetória

        # Limitar o tamanho da trajetória
        if len(self.trajectory) > self.trajectory_lifetime:
            self.trajectory.pop(0)  # Remove o primeiro ponto quando o limite é atingido

    def manageWallCollision(self, screen_width, screen_height):
        """
        Detecta e trata colisões da bola com as paredes.
        Reverte a direção da velocidade quando ocorre uma colisão.
        :param screen_width: Largura da tela.
        :param screen_height: Altura da tela.
        """
        if self.pos[0] + self.radius >= screen_width and self.v[0] > 0:
            self.v[0] *= -1
        if self.pos[0] - self.radius <= 0 and self.v[0] < 0:
            self.v[0] *= -1
        if self.pos[1] + self.radius >= screen_height and self.v[1] > 0:
            self.v[1] *= -1
        if self.pos[1] - self.radius <= 0 and self.v[1] < 0:
            self.v[1] *= -1

def r_pos(obj):
    """
    Gera uma posição aleatória para a bola dentro dos limites da tela.
    :param bola: Objeto bola para o qual a posição será gerada.
    :return: Posição aleatória como um vetor pygame.math.Vector2.
    """
    x = randint(0 + obj.radius, WIDTH - obj.radius)
    y = randint(0 + obj.radius, LENGTH - obj.radius)
    pos = pygame.math.Vector2(x, y)
    return pos

def separa_bolas(obj1, obj2):
    """ 
    Ajusta as posições das bolas para que não se sobreponham após uma colisão.
    :parâmetro obj1: Primeira bola.
    :parâmetro obj2: Segunda bola.
    """
    distance = math.hypot(obj1.pos[0] - obj2.pos[0], obj1.pos[1] - obj2.pos[1])
    offset = obj1.radius + obj2.radius - distance
    dx = (obj1.pos[0] - obj2.pos[0]) / distance * offset
    dy = (obj1.pos[1] - obj2.pos[1]) / distance * offset
    obj1.pos[0] += dx / 2
    obj1.pos[1] += dy / 2
    obj2.pos[0] -= dx / 2
    obj2.pos[1] -= dy / 2

def verificar_colisao_bolas(obj1, obj2):
    """
    Verifica se houve uma colisão entre duas bolas. 
    Em caso afirmativo, calcula as novas velocidades com base na conservação do momento linear.
    :param bola1: Primeira bola.
    :param bola2: Segunda bola.
    """
    distance = math.hypot(obj1.pos[0] - obj2.pos[0], obj1.pos[1] - obj2.pos[1])
    if distance <= obj1.radius + obj2.radius:
        # Conservação de momento linear em 2D
        v1 = obj1.v
        v2 = obj2.v
        x1 = obj1.pos
        x2 = obj2.pos
        m1 = obj1.mass
        m2 = obj2.mass
        
        # Velocidade após colisão (equações de conservação de momento)
        v1_new = v1 - (2 * m2 / (m1 + m2)) * pygame.math.Vector2.project((v1 - v2), (x1 - x2))
        v2_new = v2 - (2 * m1 / (m1 + m2)) * pygame.math.Vector2.project((v2 - v1), (x2 - x1))
        
        obj1.v = v1_new
        obj2.v = v2_new

        # Atualizar os valores de velocidade
        obj1.vx, obj1.vy = obj1.v.x, obj1.v.y
        obj2.vx, obj2.vy = obj2.v.x, obj2.v.y

        separa_bolas(obj1, obj2)

def menu_inicial():
    """ 
    Exibe o menu inicial do jogo.
    Permite ao usuário iniciar o jogo, acessar as configurações ou sair.
    """
    font = pygame.font.Font(None, 48)
    texto_iniciar = font.render("Pressione Enter para Iniciar", True, (255, 255, 255))
    texto_configurar = font.render("Pressione C para Configurar", True, (255, 255, 255))
    texto_esc = font.render("Pressione ESC para Sair", True, (255, 255, 255))  # Legenda ESC para sair
    window.fill((0, 0, 0))
    window.blit(texto_iniciar, (WIDTH // 4, LENGTH // 3))
    window.blit(texto_configurar, (WIDTH // 4, LENGTH // 2))
    window.blit(texto_esc, (WIDTH // 4, LENGTH // 1.5))  # Adicionando a legenda
    pygame.display.update()

    # Gerenciando eventos no menu inicial
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:  # Enter para iniciar o jogo
                    return "iniciar"
                if event.key == K_c:  # C para configurações
                    return "configurar"
                if event.key == K_ESCAPE:  # ESC para sair
                    pygame.quit()
                    sys.exit()

def tela_configuracoes():
    """Exibe a tela de configurações onde o usuário pode ajustar os parâmetros do jogo."""

    global MASS_MIN, MASS_MAX, V_MIN, V_MAX, N
    font = pygame.font.Font(None, 48)
    input_font = pygame.font.Font(None, 36)
    inputs = {
        "MASSA MIN": MASS_MIN,
        "MASSA MAX": MASS_MAX,
        
        "VELOCIDADE MIN": V_MIN,
        "VELOCIDADE MAX": V_MAX,
        "N": N
    }
    selected = 0
    keys = list(inputs.keys())

    def render_config():
        """
        Atualiza e renderiza a tela de configurações com as opções ajustáveis.
        """
        window.fill((0, 0, 0))
        y_pos = LENGTH // 4
        for i, key in enumerate(keys):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            value_text = input_font.render(f"{key}: {inputs[key]}", True, color)
            window.blit(value_text, (WIDTH // 4, y_pos))
            y_pos += 50

        # Texto de instrução para navegação (up/down)
        navigation_text = input_font.render("Use up/down para navegar, left/right para alterar", True, (255, 255, 255))
        window.blit(navigation_text, (WIDTH // 8, LENGTH - 100))

        # Texto de instrução para o ENTER
        enter_text = input_font.render("Pressione ENTER para salvar, e pressione novamente para rodar", True, (255, 255, 255))
        window.blit(enter_text, (WIDTH // 8, LENGTH - 60))

        # Atualiza a tela
        pygame.display.update()

    render_config()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_UP:
                    selected = (selected - 1) % len(keys)
                elif event.key == K_DOWN:
                    selected = (selected + 1) % len(keys)
                elif event.key == K_LEFT:
                    if keys[selected] == "N":
                        inputs[keys[selected]] = max(1, inputs[keys[selected]] - 1)
                    elif keys[selected].startswith("MASS"):
                        inputs[keys[selected]] = max(1, inputs[keys[selected]] - 1)
                    elif keys[selected].startswith("V"):
                        inputs[keys[selected]] = max(0, inputs[keys[selected]] - 1)
                elif event.key == K_RIGHT:
                    inputs[keys[selected]] += 1
                elif event.key == K_RETURN:
                    MASS_MIN = inputs["MASSA MIN"]
                    MASS_MAX = max(MASS_MIN, inputs["MASSA MAX"])  # Garante que MASS_MAX >= MASS_MIN
                    V_MIN = inputs["VELOCIDADE MIN"]
                    V_MAX = max(V_MIN, inputs["VELOCIDADE MAX"])  # Garante que V_MAX >= V_MIN
                    N = inputs["N"]
                    return  # Retorna ao menu principal
        render_config()


def loop_jogo():
    """
    Executa o loop principal do jogo, gerenciando as colisões e a movimentação das bolas.
    """
    global N, V_MAX, V_MIN, MASS_MAX, MASS_MIN
    list_bolas = [Bola(window) for _ in range(N)]

    i = 0
    while i < N:
        list_bolas[i].pos = r_pos(list_bolas[i])
        for j in range(0, i, 1):
            distance = math.hypot(list_bolas[i].pos[0] - list_bolas[j].pos[0], list_bolas[i].pos[1] - list_bolas[j].pos[1])
            if distance + 10 <= list_bolas[i].radius + list_bolas[j].radius:
                i = i - 1
                break
        i += 1

    run = True
    while run:
        fpsClock.tick(FPS)

        # Obter as dimensões atuais da janela
        screen_width, screen_height = window.get_size()

        for i in range(0, N - 1, 1):
            for j in range(i + 1, N, 1):
                verificar_colisao_bolas(list_bolas[i], list_bolas[j])

        for bola in list_bolas:
            bola.draw()
            bola.move()
            bola.manageWallCollision(screen_width, screen_height)

            # Desenhando a trajetória
            if len(bola.trajectory) > 1:
                for t in range(len(bola.trajectory) - 1):
                    pygame.draw.line(window, bola.color, bola.trajectory[t], bola.trajectory[t + 1], 2)

        pygame.display.update()
        window.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    menu_inicial()
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    loop_jogo()
                elif event.key == K_c:
                    tela_configuracoes()