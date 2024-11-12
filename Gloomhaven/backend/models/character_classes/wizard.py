import backend.models.action_model as action_model 
from ...utils import attack_shapes as shapes
import backend.models.obstacle as obstacle 

cards = [
    action_model.ActionCard(
        attack_name="Fireball",
        actions=[action_model.ElementAreaEffectWithTarget(
            shape=shapes.circle(1),
            element_type=obstacle.Fire,
            att_range=4
        )],
        movement=2,
        jump=True
    ),
    action_model.ActionCard(
        attack_name="Fire and Ice",
        actions=[
            action_model.AreaAttack(
                shape=shapes.cone(3),
                strength=2
            ),
            action_model.ElementAreaEffectFromSelf(
                shape=shapes.circle(2),
                element_type=obstacle.Ice,
            )
        ],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Elementary Missile",
        actions=[action_model.SingleTargetAttack(
            strength=6,
            att_range=4
        )],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Scholar's Escape",
        actions=[action_model.SingleTargetAttack(
            strength=3,
            att_range=1
        )],
        movement=5,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Masochistic Explosion",
        actions=[action_model.ElementAreaEffectFromSelf(
            element_type=obstacle.Fire,
            shape=shapes.circle(2)),
            action_model.AreaAttack(shape=shapes.circle(2),strength=3),
            action_model.ModifySelfHealth(-3)
        ],
        movement=3,
        jump=True
    ),
    action_model.ActionCard(
        attack_name="Lightning Charge",
        actions=[action_model.AreaAttack(
            shape=shapes.line((1,0), 3),
            strength=4),
            action_model.ModifySelfHealth(3)
            ],
        movement=1,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Random Teleport",
        actions=[
            action_model.SingleTargetAttack(
                strength=3,
                att_range=1
            ),
            action_model.Teleport(
                att_range=1
            ),
        ],
        movement=2,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="B-Line",
        actions=[action_model.AreaAttack(
            shape=shapes.line((0,1), 3),
            strength=4
        )],
        movement=2,
        jump=True
    ),
]

backstory = "wizards are cool"

health = 6
