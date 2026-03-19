from fastapi import APIRouter, HTTPException, Depends
from app.schemas import RegisterRequest, LoginRequest, UserPublic, AuthResponse
from app.database import get_db
from app.auth import hash_password, verify_password, create_token, get_current_user_id

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(data: RegisterRequest):
    if len(data.name.strip()) < 2:
        raise HTTPException(400, "El nombre debe tener al menos 2 caracteres")
    if len(data.password) < 6:
        raise HTTPException(400, "La contraseña debe tener al menos 6 caracteres")

    with get_db() as conn:
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE email = %s", (data.email.lower().strip(),))
        if cur.fetchone():
            raise HTTPException(409, "Este correo ya está registrado")

        hashed = hash_password(data.password)
        cur.execute(
            """INSERT INTO users (name, email, password)
               VALUES (%s, %s, %s)
               RETURNING id, name, email, avatar, created_at""",
            (data.name.strip(), data.email.lower().strip(), hashed),
        )
        row = cur.fetchone()

    user = UserPublic(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        avatar=row["avatar"],
        createdAt=row["created_at"].isoformat(),
    )
    token = create_token(user.id)
    return AuthResponse(user=user, token=token)


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, email, password, avatar, created_at FROM users WHERE email = %s",
            (data.email.lower().strip(),),
        )
        row = cur.fetchone()

    if not row or not verify_password(data.password, row["password"]):
        raise HTTPException(401, "Credenciales incorrectas")

    user = UserPublic(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        avatar=row["avatar"],
        createdAt=row["created_at"].isoformat(),
    )
    token = create_token(user.id)
    return AuthResponse(user=user, token=token)


@router.get("/profile", response_model=UserPublic)
def profile(user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, email, avatar, created_at FROM users WHERE id = %s::uuid",
            (user_id,),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuario no encontrado")

    return UserPublic(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        avatar=row["avatar"],
        createdAt=row["created_at"].isoformat(),
    )
