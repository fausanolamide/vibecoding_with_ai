from manim import *
from manim import (
    Scene,
    VGroup,
    Circle,
    Line,
    RoundedRectangle,
    Rectangle,
    Text,
    AnimationGroup,
    AddTextLetterByLetter,
    FadeIn,
    FadeOut,
    Restore,
    Transform,
    SurroundingRectangle,
    Create,
    WHITE,
    GRAY,
    BOLD,
    ORIGIN,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    PI,
    config,
    rush_into,
)

# Configure vertical 9:16 resolution for YouTube Shorts / TikTok / Reels
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = "#0D0E15"


class ExpressiveStickman(VGroup):
    """Articulated 2D stickman with laptop, coffee mug, sunglasses, and expressions."""
    def __init__(self, color=WHITE, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.head = Circle(radius=0.34, color=color, stroke_width=6).move_to(UP * 1.25)
        self.body = Line(self.head.get_bottom(), DOWN * 0.25, color=color, stroke_width=6)

        init_shoulder = self.body.point_from_proportion(0.28)
        init_hip = self.body.get_end()

        self.left_arm = Line(init_shoulder, init_shoulder + LEFT * 0.55 + DOWN * 0.45, color=color, stroke_width=6)
        self.right_arm = Line(init_shoulder, init_shoulder + RIGHT * 0.55 + DOWN * 0.45, color=color, stroke_width=6)
        self.left_leg = Line(init_hip, init_hip + LEFT * 0.38 + DOWN * 1.15, color=color, stroke_width=6)
        self.right_leg = Line(init_hip, init_hip + RIGHT * 0.38 + DOWN * 1.15, color=color, stroke_width=6)

        # Laptop prop
        lap_base = Line(ORIGIN, RIGHT * 0.9, color="#61AFEF", stroke_width=7)
        lap_screen = Line(RIGHT * 0.9, RIGHT * 1.25 + UP * 0.7, color="#61AFEF", stroke_width=7)
        self.laptop = VGroup(lap_base, lap_screen).move_to(init_shoulder + RIGHT * 0.8 + DOWN * 0.2)

        # Sunglasses (Senior mode)
        g_l = RoundedRectangle(corner_radius=0.04, width=0.28, height=0.15, fill_color="#00E5FF", fill_opacity=1, stroke_width=0)
        g_r = RoundedRectangle(corner_radius=0.04, width=0.28, height=0.15, fill_color="#00E5FF", fill_opacity=1, stroke_width=0)
        g_bridge = Line(LEFT * 0.16, RIGHT * 0.16, color="#00E5FF", stroke_width=4)
        g_l.move_to(self.head.get_center() + LEFT * 0.14 + UP * 0.04)
        g_r.move_to(self.head.get_center() + RIGHT * 0.14 + UP * 0.04)
        g_bridge.move_to(self.head.get_center() + UP * 0.04)
        self.sunglasses = VGroup(g_l, g_r, g_bridge).set_opacity(0)

        # Coffee mug (Senior prop)
        mug_body = RoundedRectangle(corner_radius=0.06, width=0.3, height=0.38, fill_color="#E5C07B", fill_opacity=1, stroke_width=0)
        mug_handle = Circle(radius=0.12, color="#E5C07B", stroke_width=3).next_to(mug_body, RIGHT, buff=-0.05)
        self.coffee = VGroup(mug_body, mug_handle).next_to(self.left_arm.get_end(), DOWN, buff=-0.05).set_opacity(0)

        self.add(
            self.head, self.body,
            self.left_arm, self.right_arm,
            self.left_leg, self.right_leg,
            self.laptop, self.sunglasses, self.coffee
        )

    @property
    def shoulder(self):
        """Dynamically computes the current shoulder position from the body Line."""
        return self.body.point_from_proportion(0.28)

    @property
    def hip(self):
        """Dynamically computes the current hip position from the body Line."""
        return self.body.get_end()

    def typing_pose(self):
        kb = self.laptop[0].get_center()
        sh = self.shoulder
        return AnimationGroup(
            self.left_arm.animate.put_start_and_end_on(sh, kb + LEFT * 0.15 + UP * 0.05),
            self.right_arm.animate.put_start_and_end_on(sh, kb + RIGHT * 0.15 + UP * 0.12),
            run_time=0.3
        )

    def panic_arms(self):
        sh = self.shoulder
        return [
            self.left_arm.animate.put_start_and_end_on(sh, self.head.get_center() + LEFT * 0.8 + UP * 0.7),
            self.right_arm.animate.put_start_and_end_on(sh, self.head.get_center() + RIGHT * 0.8 + UP * 0.7),
        ]

    def sip_coffee_pose(self):
        self.coffee.set_opacity(1)
        sh = self.shoulder
        return AnimationGroup(
            self.left_arm.animate.put_start_and_end_on(sh, self.head.get_center() + LEFT * 0.45 + DOWN * 0.1),
            self.coffee.animate.move_to(self.head.get_center() + LEFT * 0.45 + DOWN * 0.1),
            run_time=0.45
        )


def build_indented_code(data, font_size=20, line_spacing=0.44, left_margin=-3.6, top_y=3.65, space_w=0.155):
    """Explicitly positions each line taking indentation into account so spaces never collapse."""
    group = VGroup()
    for i, (indent_spaces, text_str, color) in enumerate(data):
        mob = Text(text_str, font="Consolas", font_size=font_size, color=color)
        target_left = left_margin + indent_spaces * space_w
        mob.move_to([target_left + mob.width / 2, top_y - i * line_spacing, 0])
        group.add(mob)
    return group


class VibeCodingMemeShort(Scene):
    def start_typing(self, stickman):
        """Scene-level updater for guaranteed real-time hand typing clatter at 60fps."""
        self.stop_typing(stickman)
        self._typing_t = 0.0

        def typing_updater(dt):
            self._typing_t += dt
            t = self._typing_t
            kb = stickman.laptop[0].get_center()
            sh = stickman.shoulder
            # Prominent alternating vertical taps (±0.15 units)
            left_y = np.sin(t * 22) * 0.15 + 0.10
            right_y = np.cos(t * 22) * 0.15 + 0.10
            # Natural horizontal drifting across keyboard keys
            left_x = np.cos(t * 14) * 0.07 - 0.15
            right_x = np.sin(t * 16) * 0.07 + 0.15
            stickman.left_arm.put_start_and_end_on(sh, kb + RIGHT * left_x + UP * left_y)
            stickman.right_arm.put_start_and_end_on(sh, kb + RIGHT * right_x + UP * right_y)

        self._current_typing_updater = typing_updater
        self.add_updater(typing_updater)

    def stop_typing(self, stickman):
        """Removes the scene updater and settles hands cleanly on the laptop."""
        if hasattr(self, "_current_typing_updater") and self._current_typing_updater is not None:
            self.remove_updater(self._current_typing_updater)
            self._current_typing_updater = None
        kb = stickman.laptop[0].get_center()
        sh = stickman.shoulder
        stickman.left_arm.put_start_and_end_on(sh, kb + LEFT * 0.15 + UP * 0.05)
        stickman.right_arm.put_start_and_end_on(sh, kb + RIGHT * 0.15 + UP * 0.12)

    def construct(self):
        # =====================================================================
        # 1. VIRAL HOOK (0:00 - 0:03) - Universal iPhone & Android Safe-Zone Layout
        # =====================================================================
        # Series Badge (Frame 0 & Persistent): safely below iPhone notch / Shorts top bar
        series_pill = RoundedRectangle(
            corner_radius=0.14, width=3.4, height=0.42,
            fill_color="#252526", fill_opacity=1, stroke_color="#FFD866", stroke_width=1.5
        ).move_to(UP * 5.65)
        series_text = Text(
            "DEV PAIN • EP. 02", font="Consolas", font_size=19, color="#FFD866", weight=BOLD
        ).move_to(series_pill)
        series_badge = VGroup(series_pill, series_text)

        header_card = RoundedRectangle(
            corner_radius=0.18, width=6.6, height=1.02,
            fill_color="#181824", fill_opacity=1, stroke_color="#AB9DF2", stroke_width=3
        ).move_to(UP * 4.82)

        title_1 = Text("POV: You 'Vibe Coded' With AI", font="Consolas", font_size=23, color="#AB9DF2", weight=BOLD)
        if title_1.width > 6.0:
            title_1.scale_to_fit_width(6.0)
        title_2 = Text("And Didn't Read A Single Line...", font="Consolas", font_size=17, color=WHITE)
        if title_2.width > 6.0:
            title_2.scale_to_fit_width(6.0)
        header_text = VGroup(title_1, title_2).arrange(DOWN, buff=0.08).move_to(header_card)
        hook_banner = VGroup(header_card, header_text)

        # VS Code Editor Window Frame (width=7.0 for side safe margins)
        editor_bg = RoundedRectangle(
            corner_radius=0.18, width=7.0, height=4.6,
            fill_color="#1A1B26", fill_opacity=1, stroke_color="#2E303E", stroke_width=2
        ).move_to(UP * 1.15)

        titlebar = RoundedRectangle(
            corner_radius=0.18, width=7.0, height=0.46,
            fill_color="#14151F", fill_opacity=1, stroke_color="#2E303E", stroke_width=2
        ).move_to(editor_bg.get_top() + DOWN * 0.23)
        dot_r = Circle(radius=0.06, fill_color="#FF5F56", fill_opacity=1, stroke_width=0)
        dot_y = Circle(radius=0.06, fill_color="#FFBD2E", fill_opacity=1, stroke_width=0)
        dot_g = Circle(radius=0.06, fill_color="#27C93F", fill_opacity=1, stroke_width=0)
        window_dots = VGroup(dot_r, dot_y, dot_g).arrange(RIGHT, buff=0.10).move_to(titlebar.get_left() + RIGHT * 0.55)
        filename = Text("login_service.py", font="Consolas", font_size=17, color="#7AA2F7").move_to(titlebar)

        editor_window = VGroup(editor_bg, titlebar, window_dots, filename)

        # Stickman scaled down (0.68) and positioned above bottom UI safe zone
        stickman = ExpressiveStickman().scale(0.68).move_to(DOWN * 3.35 + LEFT * 0.25)

        self.add(series_badge, hook_banner, editor_window, stickman)
        stickman.save_state()
        self.wait(2.0)

        # =====================================================================
        # 2. ACT 1: THE VIBE CODER PROMPT & AI SPAGHETTI (0:03 - 0:11)
        # =====================================================================
        role_tag = RoundedRectangle(
            corner_radius=0.14, width=3.5, height=0.42,
            fill_color="#AB9DF2", fill_opacity=0.3, stroke_color="#AB9DF2", stroke_width=2
        ).move_to(UP * 3.92)
        role_text = Text("VIBE CODER", font="Consolas", font_size=19, color="#AB9DF2", weight=BOLD).move_to(role_tag)
        jr_badge = VGroup(role_tag, role_text)

        self.play(FadeIn(jr_badge, shift=DOWN * 0.15), stickman.typing_pose(), run_time=0.45)

        # AI Prompt Box
        prompt_box = RoundedRectangle(
            corner_radius=0.14, width=6.5, height=0.52,
            fill_color="#24283B", fill_opacity=1, stroke_color="#7AA2F7", stroke_width=2
        ).move_to(UP * 2.58)
        prompt_txt = Text('Prompt > "fix login bug fast pls"', font="Consolas", font_size=17, color="#7AA2F7").move_to(prompt_box)
        if prompt_txt.width > 6.0:
            prompt_txt.scale_to_fit_width(6.0)
        prompt_grp = VGroup(prompt_box, prompt_txt)

        self.play(FadeIn(prompt_grp, shift=DOWN * 0.2), run_time=0.4)
        self.wait(0.6)

        # The Absurd AI Generated Spaghetti (Over-engineered nightmare)
        ai_code_data = [
            (0, '# AI generated 47 lines (0 read):', '#565F89'),
            (0, 'async def meta_auth_pipeline(req):', '#F7768E'),
            (4, 'return lambda x: eval(str(x))', '#9ECE6A'),
            (0, 'while True:', '#F7768E'),
            (4, 'cache = [meta_auth_pipeline(i)', '#E0AF68'),
            (8, 'for i in range(10**9)]', '#E0AF68'),
            (4, 'exec("import antigravity")', '#BB9AF7'),
        ]

        ai_lines = build_indented_code(ai_code_data, font_size=16, line_spacing=0.36, left_margin=-3.15, top_y=1.95, space_w=0.125)

        self.start_typing(stickman)
        for line in ai_lines:
            self.play(AddTextLetterByLetter(line), run_time=0.35)
        self.stop_typing(stickman)

        # Vibe Coder hits RUN blindly
        bubble_box = RoundedRectangle(
            corner_radius=0.15, width=4.8, height=0.54,
            fill_color="#1F2335", fill_opacity=0.95, stroke_color="#9ECE6A", stroke_width=2
        ).next_to(stickman.head, UP + RIGHT, buff=0.10)
        if bubble_box.get_right()[0] > 3.4:
            bubble_box.shift(LEFT * (bubble_box.get_right()[0] - 3.4))
        bubble_text = Text('"AI wrote it, so it works! 🚀"', font="Consolas", font_size=15, color="#9ECE6A").move_to(bubble_box)
        if bubble_text.width > 4.4:
            bubble_text.scale_to_fit_width(4.4)
        bubble = VGroup(bubble_box, bubble_text)

        self.play(
            FadeIn(bubble, shift=UP * 0.2),
            stickman.animate.shift(UP * 0.22),
            run_time=0.4
        )
        self.play(stickman.animate.shift(DOWN * 0.22), run_time=0.25)
        self.wait(1.5)
        self.play(FadeOut(bubble), run_time=0.25)

        # =====================================================================
        # 3. THE DISASTER: CRITICAL MEMORY & CPU MELTDOWN (0:11 - 0:15)
        # =====================================================================
        crash_box = RoundedRectangle(
            corner_radius=0.18, width=6.8, height=1.9,
            fill_color="#3B101D", fill_opacity=0.98, stroke_color="#FF3860", stroke_width=3
        ).move_to(UP * 1.15)
        crash_icon = Text("💥 OUT OF MEMORY: CRITICAL 💥", font="Consolas", font_size=20, color="#FF3860", weight=BOLD)
        crash_err = Text("MemoryError: RAM 99.9%", font="Consolas", font_size=30, color="#FFFFFF", weight=BOLD)
        crash_sub = Text("range(10**9) ate 64GB RAM & melted CPU!", font="Consolas", font_size=17, color="#FF7A93")
        crash_content = VGroup(crash_icon, crash_err, crash_sub).arrange(DOWN, buff=0.14).move_to(crash_box)
        if crash_content.width > 6.3:
            crash_content.scale_to_fit_width(6.3)
        crash_group = VGroup(crash_box, crash_content)

        # Stickman squash & alarm
        self.play(
            FadeIn(crash_group, scale=0.9),
            stickman.animate.stretch(0.4, 1, about_point=stickman.get_bottom()).set_color("#FF3860"),
            *stickman.panic_arms(),
            run_time=0.35,
            rate_func=rush_into
        )

        # Laptop smoking puffs
        smoke1 = Circle(radius=0.14, color=GRAY, fill_opacity=0.7, stroke_width=0).move_to(stickman.laptop.get_top() + UP * 0.14)
        smoke2 = Circle(radius=0.20, color=GRAY, fill_opacity=0.5, stroke_width=0).move_to(stickman.laptop.get_top() + UP * 0.44 + RIGHT * 0.18)
        smoke = VGroup(smoke1, smoke2)
        self.play(FadeIn(smoke, shift=UP * 0.3), run_time=0.45)
        self.wait(1.2)

        # Laptop Yeet & Vibe Coder flees
        self.play(
            stickman.laptop.animate.shift(RIGHT * 6 + UP * 5).rotate(3 * PI),
            FadeOut(smoke),
            run_time=0.55
        )
        self.play(
            FadeOut(prompt_grp, shift=LEFT * 2),
            FadeOut(ai_lines, shift=LEFT * 2),
            FadeOut(crash_group, shift=DOWN * 2),
            FadeOut(jr_badge),
            stickman.animate.shift(LEFT * 6),
            run_time=0.55
        )

        # =====================================================================
        # 4. ACT 2: SENIOR DEV READS THE TRACEBACK (0:15 - 0:21)
        # =====================================================================
        stickman.restore()
        stickman.move_to(DOWN * 3.35 + RIGHT * 6)  # Off-screen right
        stickman.sunglasses.set_opacity(1)        # Wearing shades
        stickman.coffee.set_opacity(1)            # Coffee in hand

        sr_role_tag = RoundedRectangle(
            corner_radius=0.14, width=3.5, height=0.42,
            fill_color="#7AA2F7", fill_opacity=0.3, stroke_color="#7AA2F7", stroke_width=2
        ).move_to(UP * 3.92)
        sr_role_text = Text("SENIOR DEV", font="Consolas", font_size=19, color="#7AA2F7", weight=BOLD).move_to(sr_role_tag)
        sr_badge = VGroup(sr_role_tag, sr_role_text)

        self.play(
            FadeIn(sr_badge, shift=DOWN * 0.15),
            stickman.animate.move_to(DOWN * 3.35 + LEFT * 0.25),
            run_time=0.85
        )
        self.play(stickman.typing_pose(), run_time=0.3)
        self.start_typing(stickman)

        # The Actual 1-character bug: '=' instead of '=='
        sr_code_data = [
            (0, '# Senior: Actually reads the 1-line traceback...', '#565F89'),
            (0, '# The original bug was a simple typo:', '#565F89'),
            (0, 'if user.is_authenticated == True:', '#9ECE6A'),
            (4, 'return grant_access(user)', '#7AA2F7'),
        ]

        sr_lines = build_indented_code(sr_code_data, font_size=18, line_spacing=0.40, left_margin=-3.15, top_y=2.55, space_w=0.135)

        for line in sr_lines:
            self.play(AddTextLetterByLetter(line), run_time=0.45)
        self.stop_typing(stickman)

        self.wait(1.0)

        # Pro-Tip Callout Box
        tip_box = RoundedRectangle(
            corner_radius=0.14, width=6.6, height=0.56,
            fill_color="#1F2335", fill_opacity=0.95, stroke_color="#E0AF68", stroke_width=2
        ).move_to(DOWN * 1.70)
        tip_text = Text('💡 Pro Tip: Read the traceback before prompting AI!', font="Consolas", font_size=16, color="#E0AF68").move_to(tip_box)
        if tip_text.width > 6.1:
            tip_text.scale_to_fit_width(6.1)
        tip_card = VGroup(tip_box, tip_text)

        self.play(FadeIn(tip_card, shift=UP * 0.2), run_time=0.35)
        self.wait(1.8)
        self.play(FadeOut(tip_card), run_time=0.25)

        # =====================================================================
        # 5. THE WIN: WEEKEND SAVED
        # =====================================================================
        success_box = RoundedRectangle(
            corner_radius=0.18, width=6.8, height=1.20,
            fill_color="#132B1F", fill_opacity=0.98, stroke_color="#2ECC71", stroke_width=3
        ).move_to(DOWN * 1.70)
        s_title = Text("✅ OUTPUT: Login Successful (12ms)", font="Consolas", font_size=21, color="#2ECC71", weight=BOLD)
        s_sub = Text("0 Memory Leaks. Senior Leaves at 5:03 PM 🚗💨", font="Consolas", font_size=16, color=WHITE)
        success_content = VGroup(s_title, s_sub).arrange(DOWN, buff=0.12).move_to(success_box)
        if success_content.width > 6.3:
            success_content.scale_to_fit_width(6.3)
        success_card = VGroup(success_box, success_content)

        self.play(
            FadeIn(success_card, shift=UP * 0.3),
            stickman.sip_coffee_pose(),
            run_time=0.45
        )
        self.wait(2.2)

        # =====================================================================
        # 6. CLEAR SCREEN END CARD: STICKMAN + FOLLOW CTA CENTERED
        # =====================================================================
        self.stop_typing(stickman)
        cta_text = Text(
            "Follow for Ep. 3",
            font="Consolas", font_size=26, color="#78DCE8", weight=BOLD
        )
        cta_box = RoundedRectangle(
            corner_radius=0.22, width=cta_text.width + 1.1, height=0.80,
            fill_color="#1E1E1E", fill_opacity=0.98, stroke_color="#78DCE8", stroke_width=2.5
        ).move_to(UP * 0.8)
        cta_text.move_to(cta_box)
        cta_banner = VGroup(cta_box, cta_text)

        self.play(
            FadeOut(sr_lines, shift=UP * 0.3),
            FadeOut(success_card, shift=UP * 0.3),
            FadeOut(sr_badge),
            FadeOut(editor_window),
            FadeOut(hook_banner),
            stickman.animate.move_to(DOWN * 1.2 + LEFT * 0.2),
            FadeIn(cta_banner, scale=0.9),
            run_time=0.45
        )
        self.wait(1.6)

        # =====================================================================
        # 7. SEAMLESS INFINITE LOOP RESET (Matches Frame 0 Identically)
        # =====================================================================
        stickman.sunglasses.set_opacity(0)
        stickman.coffee.set_opacity(0)
        self.play(
            FadeOut(cta_banner, scale=0.9),
            FadeIn(hook_banner),
            FadeIn(editor_window),
            Restore(stickman),
            run_time=0.6
        )
        self.wait(0.2)
