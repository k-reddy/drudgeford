from gh_types import ActionCard

wizard_cards = [
    ActionCard(
            attack_name=f"Fireball",
            strength=0,
            distance=4,
            movement=2,
            status_effect="Fire",
            radius=1
    ),
    ActionCard(
            attack_name=f"Elementary Missile",
            strength=5,
            distance=4,
            movement=0,
            status_effect=None,
            radius=None
    ),
    ActionCard(
            attack_name=f"Quick Retreat",
            strength=1,
            distance=1,
            movement=5,
            status_effect=None,
            radius=None
    ),
    ActionCard(
            attack_name=f"Masochistic Explosion",
            strength=0,
            distance=1,
            movement=0,
            status_effect="Fire",
            radius=2
    ),
    ActionCard(
            attack_name=f"Magic Blast",
            strength=4,
            distance=4,
            movement=4,
            status_effect=None,
            radius=None
    )
]