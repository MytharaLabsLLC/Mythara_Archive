"""
Generate Mythara Pricing Page Video using Manim (Animation Engine)

Copyright © 2025 Herbert Velez Jr. All rights reserved.

This script creates an animated video explaining Mythara's pricing tiers
with the cute fox mascot and elegant animations.
"""

from manim import *
import os
from dotenv import load_dotenv

load_dotenv()

class MytharaPricingVideo(Scene):
    def construct(self):
        # Configuration
        self.camera.background_color = "#000000"

        # Title sequence
        self.intro_sequence()
        self.wait(1)

        # Pricing tiers
        self.show_pilot_tier()
        self.wait(2)
        self.show_growth_tier()
        self.wait(2)
        self.show_enterprise_tier()
        self.wait(2)
        self.show_sovereign_tier()
        self.wait(2)

        # Call to action
        self.call_to_action()
        self.wait(3)

    def intro_sequence(self):
        """Animated intro with Mythara branding"""
        # Title
        title = Text("Mythara Engine", font_size=72, gradient=(PURPLE, BLUE))
        subtitle = Text("Enterprise Pricing", font_size=42, color=WHITE)
        subtitle.next_to(title, DOWN, buff=0.5)

        # Fox mascot (simplified orb)
        fox = Circle(radius=1.5, color=PURPLE, fill_opacity=0.3)
        fox.set_stroke(PURPLE, width=3)
        fox_glow = Circle(radius=1.8, color=PURPLE, fill_opacity=0.1)
        fox_glow.set_stroke(PURPLE, width=1)

        # Animate
        self.play(
            FadeIn(fox_glow),
            GrowFromCenter(fox),
            run_time=1.5
        )
        self.play(
            Write(title),
            FadeIn(subtitle),
            run_time=2
        )

        # Clear screen
        self.play(
            FadeOut(title),
            FadeOut(subtitle),
            FadeOut(fox),
            FadeOut(fox_glow),
            run_time=1
        )

    def create_tier_card(self, tier_name, price, features, color):
        """Create an animated pricing tier card"""
        # Card background
        card = RoundedRectangle(
            corner_radius=0.3,
            width=10,
            height=6,
            color=color,
            fill_opacity=0.1
        )
        card.set_stroke(color, width=3)

        # Tier name
        name = Text(tier_name, font_size=48, color=color, weight=BOLD)
        name.move_to(card.get_top() + DOWN * 0.8)

        # Price
        price_text = Text(price, font_size=36, color=WHITE)
        price_text.next_to(name, DOWN, buff=0.5)

        # Features
        feature_group = VGroup()
        for i, feature in enumerate(features):
            bullet = Text("•", font_size=24, color=color)
            feat_text = Text(feature, font_size=24, color=WHITE)
            feat_line = VGroup(bullet, feat_text).arrange(RIGHT, buff=0.2)
            feature_group.add(feat_line)

        feature_group.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        feature_group.next_to(price_text, DOWN, buff=0.7)
        feature_group.shift(LEFT * 2)

        return VGroup(card, name, price_text, feature_group)

    def show_pilot_tier(self):
        """Show Pilot tier"""
        tier = self.create_tier_card(
            "Pilot",
            "$15K - $20K (30-90 days)",
            [
                "Limited invocations",
                "Full onboarding support",
                "100% credit on upgrade",
                "Proof of concept validation"
            ],
            BLUE
        )

        self.play(FadeIn(tier), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(tier), run_time=1)

    def show_growth_tier(self):
        """Show Growth tier"""
        tier = self.create_tier_card(
            "Growth",
            "$35K - $40K / year",
            [
                "Invocation cap included",
                "Standard support",
                "For scaling teams",
                "Production ready"
            ],
            GREEN
        )

        self.play(FadeIn(tier), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(tier), run_time=1)

    def show_enterprise_tier(self):
        """Show Enterprise tier (featured)"""
        tier = self.create_tier_card(
            "Enterprise",
            "$60K / year",
            [
                "100K monthly invocations",
                "Integrity artifacts included",
                "Priority bug fixes",
                "SLA guarantees",
                "Inflation-adjusted pricing"
            ],
            PURPLE
        )

        # Add "Most Popular" badge
        badge = Text("MOST POPULAR", font_size=20, color=YELLOW, weight=BOLD)
        badge.move_to(tier[0].get_corner(UR) + DOWN * 0.3 + LEFT * 1)
        badge_bg = RoundedRectangle(
            corner_radius=0.1,
            width=badge.width + 0.4,
            height=badge.height + 0.2,
            color=YELLOW,
            fill_opacity=0.2
        )
        badge_bg.move_to(badge)

        self.play(FadeIn(tier), run_time=1.5)
        self.play(FadeIn(badge_bg), Write(badge), run_time=0.8)
        self.wait(2)
        self.play(FadeOut(tier), FadeOut(badge), FadeOut(badge_bg), run_time=1)

    def show_sovereign_tier(self):
        """Show Sovereign tier"""
        tier = self.create_tier_card(
            "Sovereign / Air-Gap",
            "$150K - $180K / year",
            [
                "On-premise deployment",
                "Air-gapped infrastructure",
                "Enhanced audit controls",
                "Custom SLAs",
                "Dedicated support team"
            ],
            RED
        )

        self.play(FadeIn(tier), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(tier), run_time=1)

    def call_to_action(self):
        """Final call to action"""
        # CTA text
        cta_title = Text("Ready to get started?", font_size=48, color=WHITE)
        cta_subtitle = Text("Email MytharaLabsLLC@yahoo.com", font_size=32, color=PURPLE)
        cta_subtitle.next_to(cta_title, DOWN, buff=0.5)

        # Fox mascot returns
        fox = Circle(radius=1, color=PURPLE, fill_opacity=0.3)
        fox.set_stroke(PURPLE, width=3)
        fox.next_to(cta_subtitle, DOWN, buff=1)

        # Animate
        self.play(
            Write(cta_title),
            run_time=1.5
        )
        self.play(
            FadeIn(cta_subtitle),
            GrowFromCenter(fox),
            run_time=1.5
        )

        # Pulsing effect
        self.play(
            fox.animate.scale(1.2).set_opacity(0.8),
            rate_func=there_and_back,
            run_time=1
        )


# For voice narration sync (optional)
class MytharaPricingWithVoice(MytharaPricingVideo):
    """Extended version that syncs with ElevenLabs voice narration"""

    def __init__(self, audio_file=None, **kwargs):
        super().__init__(**kwargs)
        self.audio_file = audio_file or "core/static/mythara-pricing-voice.mp3"

    def construct(self):
        # Add background music/narration if available
        if os.path.exists(self.audio_file):
            self.add_sound(self.audio_file)

        # Run normal animation
        super().construct()


if __name__ == "__main__":
    print("🎬 Mythara Pricing Video Generator")
    print("=" * 50)
    print()
    print("This script uses Manim to create an animated pricing video.")
    print()
    print("To render the video, run:")
    print("  manim -pql generate_pricing_video.py MytharaPricingVideo")
    print()
    print("For high quality:")
    print("  manim -pqh generate_pricing_video.py MytharaPricingVideo")
    print()
    print("With voice narration:")
    print("  manim -pqh generate_pricing_video.py MytharaPricingWithVoice")
    print()
    print("Output will be in: media/videos/generate_pricing_video/")
    print()
