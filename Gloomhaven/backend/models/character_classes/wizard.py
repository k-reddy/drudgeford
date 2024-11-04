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
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Cursed Frost Surge",
        actions=[
            action_model.AreaAttack(
                shape=shapes.bar(1,2),
                strength=1
            ),
            action_model.ElementAreaEffectFromSelf(
                shape=shapes.bar(1,2),
                element_type=obstacle.Ice,
            )
        ],
        movement=2,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Elementary Missile",
        actions=[action_model.SingleTargetAttack(
            strength=5,
            att_range=4
        )],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Scholar's Escape",
        actions=[action_model.SingleTargetAttack(
            strength=1,
            att_range=1
        )],
        movement=5,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Masochistic Explosion",
        actions=[action_model.ElementAreaEffectFromSelf(
            element_type=obstacle.Fire,
            shape=shapes.circle(2)
        )],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Lightning Bolt",
        actions=[action_model.AreaAttack(
            shape=shapes.line((1,0), 3),
            strength=4
        )],
        movement=1,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Random Teleport",
        actions=[
            action_model.Teleport(
                att_range=1
            ),
            action_model.SingleTargetAttack(
                strength=2,
                att_range=1
            )
        ],
        movement=1,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="B-Line",
        actions=[action_model.AreaAttack(
            shape=shapes.line((0,1), 2),
            strength=2
        )],
        movement=2,
        jump=True
    ),
]

backstory = "wizards are cool"

health = 6
