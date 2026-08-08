from app.growth.recommendation_renderer import RecommendationRenderer
from app.growth.status_renderer import StatusRenderer
from app.growth.system_status import Check


def test_status_renderer_hides_meta_token_name():
    renderer = StatusRenderer()
    text = renderer.render(
        [
            Check("Meta", False, "не настроен — META_VERIFY_TOKEN"),
        ],
        limit=4096,
    )

    assert "META_VERIFY_TOKEN" not in text
    assert "Meta Business is not connected" in text


def test_recommendation_renderer_provides_actionable_steps():
    recommendations = RecommendationRenderer().for_status(
        [
            Check("Doctor", False, "2 problems"),
            Check("Deploy", False, "outdated"),
            Check("Git", False, "dirty"),
            Check("Docker", False, "down"),
            Check("Meta", False, "not configured"),
        ]
    )

    assert any("scripts/doctor.sh" in item for item in recommendations)
    assert any("./deploy.sh" in item for item in recommendations)
    assert any("git" in item.lower() for item in recommendations)
    assert any("containers" in item.lower() for item in recommendations)
    assert any("Meta Business" in item for item in recommendations)
