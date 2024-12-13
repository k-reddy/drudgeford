import backend.models.action_model as action_model
from ...utils import attack_shapes as shapes
import backend.models.obstacle as obstacle

cards = [
    action_model.ActionCard(
        attack_name="Fireball",
        actions=[
            action_model.AreaAttackWithTarget(
                shape=shapes.circle(1),
                element_type=obstacle.Fire,
                att_range=4,
                damage=3,
            )
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Fire and Ice",
        actions=[
            action_model.AreaAttackWithTarget(
                shape=shapes.cone(2), att_range=2, damage=2, element_type=obstacle.Fire
            ),
            action_model.AreaAttackWithTarget(
                shape=shapes.cone(2), att_range=2, damage=2, element_type=obstacle.Ice
            ),
        ],
        movement=3,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Elementary Missile",
        actions=[action_model.SingleTargetAttack(strength=6, att_range=4)],
        movement=0,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Scholar's Escape",
        actions=[action_model.Fortify(3)],
        movement=5,
        jump=True,
    ),
    action_model.ActionCard(
        attack_name="Masochistic Explosion",
        actions=[
            action_model.AreaAttackFromSelf(
                element_type=obstacle.Fire, shape=shapes.circle(2), strength=5
            ),
            action_model.ModifySelfHealth(-3),
        ],
        movement=3,
        jump=True,
    ),
    action_model.ActionCard(
        attack_name="Lightning Charge",
        actions=[
            action_model.AreaAttackWithTarget(
                shape=shapes.line(3), damage=3, att_range=2
            ),
            action_model.ModifySelfHealth(3),
        ],
        movement=1,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Random Teleport",
        actions=[
            action_model.SingleTargetAttack(strength=2, att_range=1),
            action_model.Teleport(att_range=1),
            action_model.Teleport(att_range=1),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Phase Strike",
        actions=[
            action_model.AreaAttackWithTarget(
                shape=shapes.bar(1, 2), damage=3, att_range=3
            )
        ],
        movement=2,
        jump=True,
    ),
]

backstory = """Raised by overbearing parents who demanded magical excellence from a young age, this young wizard spent their childhood studying ancient texts while other kids played outside. Now an Acolyte, they channel their isolation and academic pressure into devastating spells, forever striving to reach Arch Mage status to finally earn parental approval. Their magical prowess is matched only by their social awkwardness and determination to prove themselves worthy. A glass cannon spellcaster who controls the battlefield from range with powerful elemental attacks."""

health = 6
