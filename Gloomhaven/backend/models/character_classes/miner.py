import backend.models.action_model as action_model
from ...utils import attack_shapes as shapes
from backend.models.obstacle import Rock


cards = [
    action_model.ActionCard(
        attack_name="Heavy Hammer",
        actions=[
            action_model.SingleTargetAttack(strength=5, att_range=1, knock_down=True),
            action_model.ChargeNextAttack(strength=2),
        ],
        movement=0,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Pickaxe Swipe",
        actions=[action_model.AreaAttackFromSelf(shape=shapes.arc(3), strength=4)],
        movement=3,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Mason's Shield",
        actions=[
            action_model.ShieldSelf(strength=2, duration=2),
            action_model.SingleTargetAttack(strength=4, att_range=1),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Stone Meditation",
        actions=[
            action_model.ShieldSelf(strength=2, duration=1),
            action_model.ModifySelfHealth(strength=4),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Crystal Ward",
        actions=[
            action_model.ModifySelfHealth(strength=4),
            action_model.AreaAttackFromSelf(shapes.ring(2), 2),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Self Sacrifice",
        actions=[
            action_model.SingleTargetAttack(strength=6, att_range=1),
            action_model.BlessSelf(),
            action_model.ModifySelfHealth(-4),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Desperate Mining",
        actions=[
            action_model.AreaAttackFromSelf(shape=shapes.bar(1, 2), strength=3),
            action_model.BlessSelf(),
            action_model.ChargeNextAttack(strength=4),
            action_model.ModifySelfHealth(-3),
        ],
        movement=0,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Tax Assessment",
        actions=[
            action_model.Pull(squares=2, att_range=3),
            action_model.SingleTargetAttack(strength=3, att_range=1, knock_down=True),
            action_model.WeakenEnemy(strength=-2, att_range=1),
        ],
        movement=2,
        jump=False,
    ),
    action_model.ActionCard(
        attack_name="Stone Defense",
        actions=[
            action_model.MakeObstableArea(obstacle_type=Rock, shape=shapes.bar(1, 1)),
            action_model.ShieldAllAllies(strength=2, duration=1, att_range=2),
        ],
        movement=3,
        jump=False,
    ),
]
backstory = """A former tax auditor turned mason with an obsession for crystals, driven to the mountains by her passionate belief in their power. Her journey began when a debtor introduced her to the mystical world of crystal energy. Now incredibly strong from years of mining, she uses her power to collect ever more precious gems. Though others mock her new-age beliefs, her connection to the stones only grows stronger - as does her ability to wield her tools in combat. A durable melee fighter who packs big punches while preserving their health with shields and healing crystals."""

health = 16
