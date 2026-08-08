from app.security.passwords import hash_password, verify_password


def test_password_no_se_guarda_en_claro() -> None:
    hashed = hash_password("correcta-123")
    assert hashed != "correcta-123"
    assert verify_password("correcta-123", hashed)
    assert not verify_password("incorrecta", hashed)
