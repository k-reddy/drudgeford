from gh_types import ActionCard
import attack_shapes as shapes

cards = [
    ActionCard(
        attack_name=f"Fireball",
        strength=0,
        distance=4,
        movement=2,
        status_effect="Fire",
        status_shape=shapes.circle(1),
        jump=False
    ),
    ActionCard(
        attack_name=f"Cursed Frost Surge",
        strength=0,
        distance=4,
        movement=2,
        status_effect="Ice",
        status_shape=shapes.circle(1),
        jump=False
    ),
    ActionCard(
        attack_name=f"Elementary Missile",
        strength=5,
        distance=4,
        movement=0,
        status_effect=None,
        status_shape=None,
        jump=False
    ),
    ActionCard(
        attack_name=f"Quick Retreat",
        strength=1,
        distance=1,
        movement=5,
        status_effect=None,
        status_shape=None,
        jump=False
    ),
    ActionCard(
        attack_name=f"Masochistic Explosion",
        strength=0,
        distance=1,
        movement=0,
        status_effect="Fire",
        status_shape=shapes.circle(2),
        jump=False
    ),
    ActionCard(
        attack_name=f"Magic Blast",
        strength=4,
        distance=4,
        movement=4,
        status_effect=None,
        status_shape=None,
        jump=True
    ),
]

backstory = ""

health = 6
