import action_model
import attack_shapes as shapes
from obstacle import Rock


cards = [
    action_model.ActionCard(
        attack_name="Heavy Hammer",
        actions=[
            action_model.SingleTargetAttack(
                strength=4,
                att_range=1
            ),
            action_model.ChargeNextAttack(
                strength=2
            )
        ],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Pickaxe Swipe",
        actions=[
            action_model.AreaAttack(
                shape=shapes.arc(4),
                strength=2
            )
        ],
        movement=2,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Mason's Shield",
        actions=[
            action_model.ShieldSelf(
                strength=1,
                duration=2
            ),
            action_model.SingleTargetAttack(
                strength=4,
                att_range=1
            )
        ],
        movement=2,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Stone Meditation",
        actions=[
            action_model.ShieldSelf(
                strength=2,
                duration=1
            ),
            action_model.ModifySelfHealth(
                strength=4
            )
        ],
        movement=1,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Crystal Placebo",
        actions=[
            action_model.ModifySelfHealth(strength=4),
            action_model.SingleTargetAttack(
                strength=2,
                att_range=1
            ),
        ],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Self Sacrifice",
        actions=[
            action_model.SingleTargetAttack(
                strength=6,
                att_range=1
            ),
            action_model.BlessSelf(),
            action_model.ModifySelfHealth(-4)
        ],
        movement=1,
        jump=False   
    ),
    action_model.ActionCard(
        attack_name="Desperate Mining",
        actions=[
            action_model.AreaAttack(shape=shapes.circle(2),strength=1),
            action_model.BlessSelf(),
            action_model.ChargeNextAttack(strength=4),
            action_model.ModifySelfHealth(-5),
        ],
        movement=0,
        jump=False
    ),
    action_model.ActionCard(
        # Tax Assessment - Weaken target, pull 2, attack 3
        attack_name="Tax Assessment",
        actions=[
            action_model.Pull(
                squares=2, 
                att_range=3
            ),
            action_model.SingleTargetAttack(
                strength=3,
                att_range=1
            ),
            action_model.WeakenEnemy(
                strength=-2,
                att_range=1
            )
        ],
        movement=3,
        jump=False
    ),
    action_model.ActionCard(
        attack_name="Stone Defense",
        actions=[
            action_model.MakeObstableArea(
                obstacle_type=Rock,
                shape=shapes.bar(1,1)
            ),
            action_model.ShieldAllAllies(
                strength=2,
                duration=1,
                att_range=2
            )
        ],
        movement=0,
        jump=False
    )
]
backstory = "I'm a miner"
health = 16