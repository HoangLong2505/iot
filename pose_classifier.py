import math


def calculate_angle(a, b, c):
    """Tính góc (độ) tại điểm b, tạo bởi 3 điểm a, b, c"""
    ba_x, ba_y = a[0] - b[0], a[1] - b[1]
    bc_x, bc_y = c[0] - b[0], c[1] - b[1]

    dot = ba_x * bc_x + ba_y * bc_y
    mag1 = math.sqrt(ba_x ** 2 + ba_y ** 2)
    mag2 = math.sqrt(bc_x ** 2 + bc_y ** 2)

    if mag1 == 0 or mag2 == 0:
        return 0

    cos_angle = dot / (mag1 * mag2)
    cos_angle = max(-1, min(1, cos_angle))
    return math.degrees(math.acos(cos_angle))


def get_mid_point(p1, p2):
    """Tính điểm ở giữa an toàn nếu có ít nhất 1 điểm hiển thị"""
    pts = []
    if p1[0] > 0 and p1[1] > 0: pts.append(p1)
    if p2[0] > 0 and p2[1] > 0: pts.append(p2)
    if not pts: return None
    return [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]


def classify_pose(person):
    valid = person[(person[:, 0] > 0) & (person[:, 1] > 0)]
    if len(valid) < 8:
        return "UNKNOWN"

    # Thông số khung bao (Bounding Box)
    min_x, max_x = valid[:, 0].min(), valid[:, 0].max()
    min_y, max_y = valid[:, 1].min(), valid[:, 1].max()

    body_width = max_x - min_x
    body_height = max_y - min_y
    ratio = body_width / (body_height + 1e-6)

    # Lấy tọa độ các điểm quan trọng
    head_y = person[0][1]
    ankle_y = max(person[15][1], person[16][1])

    mid_shoulder = get_mid_point(person[5], person[6])
    mid_hip = get_mid_point(person[11], person[12])
    mid_knee = get_mid_point(person[13], person[14])
    mid_ankle = get_mid_point(person[15], person[16])

    # ======================
    # 1. FALL (Ngã / Nằm)
    # ======================
    # Thay 120 pixel bằng 20% chiều cao cơ thể (Tránh lỗi do đứng xa/gần)
    head_near_floor = head_y > ankle_y - (body_height * 0.2) if (ankle_y > 0 and head_y > 0) else False
    if head_near_floor or ratio > 0.7:
        return "FALL"

    # ======================
    # 2. BENDING (Gập người)
    # ======================
    if mid_shoulder and mid_hip and mid_knee:
        hip_angle = calculate_angle(mid_shoulder, mid_hip, mid_knee)
        if 0 < hip_angle < 150:
            return "BENDING"
    elif mid_shoulder and mid_hip:
        dx = abs(mid_hip[0] - mid_shoulder[0])
        dy = abs(mid_hip[1] - mid_shoulder[1]) + 1e-6
        if math.degrees(math.atan(dx / dy)) > 40:
            return "BENDING"

    # ======================
    # 3. SITTING (Ngồi)
    # ======================
    # Logic mới không dùng pixel cố định. Dùng góc đầu gối và tỷ lệ đùi.

    # Cách A: Dựa vào góc gập của đầu gối (Hông - Đầu gối - Mắt cá chân)
    if mid_hip and mid_knee and mid_ankle:
        knee_angle = calculate_angle(mid_hip, mid_knee, mid_ankle)
        # Người ngồi thường có góc đầu gối gập lại dưới 140 độ
        if 0 < knee_angle < 140:
            return "SITTING"
            # Cách B: Dự phòng nếu bị khuất chân, so sánh chiều cao đùi và lưng
            if mid_shoulder and mid_hip and mid_knee:
                torso_h = mid_hip[1] - mid_shoulder[1]
                thigh_h = mid_knee[1] - mid_hip[1]

                # Khi ngồi, đùi nằm ngang nên chiều cao theo trục Y rất ngắn.
                # Kết hợp khung bao phải hơi vuông (ratio > 0.4) để tránh nhầm lúc đang bước đi.
                if thigh_h > 0 and torso_h > 0:
                    if thigh_h < torso_h * 0.5 and ratio > 0.4:
                        return "SITTING"

            # ======================
            # 4. STANDING (Đứng)
            # ======================
        return "STANDING"
