import backend.models.action_model as action_model
from ...utils import attack_shapes as shapes
import backend.models.obstacle as obstacle

cards = [
    action_model.ActionCard(
        attack_name="Fireball",
        actions=[
            action_model.ElementAreaEffectWithTarget(
                shape=shapes.circle(1),
                element_type=obstacle.Fire,
                att_range=4,
            ),
            action_model.SingleTargetAttack(3, 4),
        ],
        movement=2,
        jump=True,
    ),
    action_model.ActionCard(
        attack_name="Fire and Ice",
        actions=[
            action_model.AreaAttack(shape=shapes.cone(3), strength=2),
            action_model.ElementAreaEffectFromSelf(
                shape=shapes.cone(3), element_type=obstacle.Fire
            ),
            action_model.ElementAreaEffectFromSelf(
                shape=shapes.circle(2),
                element_type=obstacle.Ice,
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
        actions=[action_model.SingleTargetAttack(strength=3, att_range=1)],
        movement=5,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Masochistic Explosion",
        actions=[
            action_model.ElementAreaEffectFromSelf(
                element_type=obstacle.Fire, shape=shapes.circle(2)
            ),
            action_model.AreaAttack(shape=shapes.circle(2), strength=5),
        ],
        movement=3,
        jump=True,
    ),
    action_model.ActionCard(
        attack_name="Lightning Charge",
        actions=[
            action_model.AreaAttack(shape=shapes.line((1, 0), 3), strength=4),
            action_model.ModifySelfHealth(3),
        ],
        movement=1,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Random Teleport",
        actions=[
            action_model.SingleTargetAttack(strength=3, att_range=1),
            action_model.Teleport(att_range=1),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="B-Line",
        actions=[action_model.AreaAttack(shape=shapes.line((0, 1), 3), strength=4)],
        movement=2,
        jump=True,
    ),
]

backstory = """Raised by overbearing parents who demanded magical excellence from a young age, this young wizard spent their childhood studying ancient texts while other kids played outside. Now an Acolyte, they channel their isolation and academic pressure into devastating spells, forever striving to reach Arch Mage status to finally earn parental approval. Their magical prowess is matched only by their social awkwardness and determination to prove themselves worthy. A glass cannon spellcaster who controls the battlefield from range with powerful elemental attacks."""

health = 6
