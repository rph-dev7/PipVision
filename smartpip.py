import time
import math
import pyautogui
import pygetwindow as gw
import win32gui
import win32con

# =========================
# CONFIGURAÇÕES
# =========================

DETECTION_DISTANCE = 500
FORCE = 7.0
FRICTION = 0.92
MAX_SPEED = 140
FPS = 120

# margem da tela
SCREEN_MARGIN = 10

# velocidade acumulada
velocity_x = 0.0
velocity_y = 0.0

# cooldown para evitar spam
last_move_time = 0
MOVE_DELAY = 0.008


# =========================
# ENCONTRAR JANELA PIP
# =========================

def get_pip_window():
    windows = gw.getWindowsWithTitle("Picture-in-picture")

    if not windows:
        windows = gw.getWindowsWithTitle("Picture in Picture")

    if not windows:
        windows = gw.getWindowsWithTitle("Picture")

    if not windows:
        return None

    return windows[0]


# =========================
# FIXAR SEMPRE NO TOPO
# =========================

def make_topmost(window):
    try:
        hwnd = window._hWnd

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE |
            win32con.SWP_NOSIZE |
            win32con.SWP_SHOWWINDOW
        )

    except:
        pass


# =========================
# LIMITAR NA TELA
# =========================

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


# =========================
# LOOP PRINCIPAL
# =========================

print("Abra o PiP.")

screen_w, screen_h = pyautogui.size()

while True:

    try:

        window = get_pip_window()

        if window is None:
            time.sleep(1)
            continue

        make_topmost(window)

        now = time.time()

        if now - last_move_time < MOVE_DELAY:
            time.sleep(0.001)
            continue

        # =========================
        # DADOS DO MOUSE
        # =========================

        mouse_x, mouse_y = pyautogui.position()

        # =========================
        # DADOS DA JANELA
        # =========================

        left = window.left
        top = window.top
        width = window.width
        height = window.height

        center_x = left + width / 2
        center_y = top + height / 2

        # =========================
        # DISTÂNCIA
        # =========================

        dx = center_x - mouse_x
        dy = center_y - mouse_y

        distance = math.sqrt(dx * dx + dy * dy)

        # =========================
        # REPELIR MOUSE
        # =========================

        if distance < DETECTION_DISTANCE:

            # evitar divisão por zero
            if distance == 0:
                distance = 0.1

            # normalização do vetor
            nx = dx / distance
            ny = dy / distance

            # intensidade proporcional
            strength = (
                (DETECTION_DISTANCE - distance)
                / DETECTION_DISTANCE
            )

            # aceleração
            velocity_x += nx * FORCE * strength * 8
            velocity_y += ny * FORCE * strength * 8

        # =========================
        # ATRITO
        # =========================

        velocity_x *= FRICTION
        velocity_y *= FRICTION

        # =========================
        # LIMITAR VELOCIDADE
        # =========================

        velocity_x = clamp(
            velocity_x,
            -MAX_SPEED,
            MAX_SPEED
        )

        velocity_y = clamp(
            velocity_y,
            -MAX_SPEED,
            MAX_SPEED
        )

        # =========================
        # NOVA POSIÇÃO
        # =========================

        new_x = int(left + velocity_x)
        new_y = int(top + velocity_y)

        # =========================
        # IMPEDIR SAIR DA TELA
        # =========================

        new_x = clamp(
            new_x,
            SCREEN_MARGIN,
            screen_w - width - SCREEN_MARGIN
        )

        new_y = clamp(
            new_y,
            SCREEN_MARGIN,
            screen_h - height - SCREEN_MARGIN
        )

        # =========================
        # MOVER JANELA
        # =========================

        window.moveTo(new_x, new_y)

        last_move_time = now

        # =========================
        # FPS
        # =========================

        time.sleep(1 / FPS)

    except KeyboardInterrupt:
        print("Encerrado.")
        break

    except Exception as e:
        print("ERRO:", e)
        time.sleep(1)