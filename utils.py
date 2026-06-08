import math

def calculate_angle(a, b, c):
    ba_x = a[0] - b[0]
    ba_y = a[1] - b[1]

    bc_x = c[0] - b[0]
    bc_y = c[1] - b[1]

    dot = ba_x * bc_x + ba_y * bc_y

    mag1 = math.sqrt(
        ba_x**2 + ba_y**2
    )

    mag2 = math.sqrt(
        bc_x**2 + bc_y**2
    )

    if mag1 == 0 or mag2 == 0:
        return 0

    cos_angle = dot / (mag1 * mag2)

    cos_angle = max(
        -1,
        min(1, cos_angle)
    )

    angle = math.degrees(
        math.acos(cos_angle)
    )

    return angle


def body_angle(person):
    left_shoulder = person[5]
    right_shoulder = person[6]

    left_hip = person[11]
    right_hip = person[12]

    shoulder_x = (
        left_shoulder[0]
        + right_shoulder[0]
    ) / 2

    shoulder_y = (
        left_shoulder[1]
        + right_shoulder[1]
    ) / 2

    hip_x = (
        left_hip[0]
        + right_hip[0]
    ) / 2

    hip_y = (
        left_hip[1]
        + right_hip[1]
    ) / 2

    dx = hip_x - shoulder_x
    dy = hip_y - shoulder_y

    angle = abs(
        math.degrees(
            math.atan2(dx, dy)
        )
    )

    return angle