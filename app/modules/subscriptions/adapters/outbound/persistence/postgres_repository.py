from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.application.errors import ConflictError, RepositoryError


class SqlAlchemySubscriptionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create_subscriber_with_payment(
        self,
        dni: str,
        first_names: str,
        last_names: str,
        phone: str,
        email: str,
        password_hash: str,
        valid_from: date,
        valid_until: date,
        receipt_path: str,
        validated_by: UUID,
        amount: Decimal,
    ) -> UUID:
        try:
            result = self._db.execute(
                text(
                    """
                    INSERT INTO uce.core_persons (
                        dni,
                        dni_type,
                        first_names,
                        last_names,
                        name,
                        phone,
                        email,
                        password_hash,
                        person_type,
                        must_change_password
                    )
                    VALUES (
                        :dni,
                        'CEDULA',
                        :first_names,
                        :last_names,
                        :name,
                        :phone,
                        :email,
                        :password_hash,
                        'SUSCRIPTOR',
                        true
                    )
                    RETURNING id
                    """
                ),
                {
                    "dni": dni,
                    "first_names": first_names,
                    "last_names": last_names,
                    "name": f"{first_names} {last_names}".strip(),
                    "phone": phone,
                    "email": email,
                    "password_hash": password_hash,
                },
            )
            person_id = result.scalar_one()

            self._db.execute(
                text(
                    """
                    INSERT INTO uce.payments (
                        person_id,
                        amount,
                        valid_from,
                        valid_until,
                        receipt_path,
                        status,
                        validated_by
                    )
                    VALUES (
                        :person_id,
                        :amount,
                        :valid_from,
                        :valid_until,
                        :receipt_path,
                        'VALIDADO',
                        :validated_by
                    )
                    """
                ),
                {
                    "person_id": str(person_id),
                    "amount": amount,
                    "valid_from": valid_from,
                    "valid_until": valid_until,
                    "receipt_path": receipt_path,
                    "validated_by": str(validated_by),
                },
            )
            self._db.commit()
            return person_id
        except IntegrityError as exc:
            self._db.rollback()
            raise ConflictError("El DNI o el correo ya existen.") from exc
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise RepositoryError("Error al registrar el suscriptor y su pago.") from exc

    def has_valid_subscription(self, person_id: UUID) -> bool:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM uce.payments
                        WHERE person_id = :person_id
                          AND status = 'VALIDADO'
                          AND current_date BETWEEN valid_from AND valid_until
                    )
                    """
                ),
                {"person_id": str(person_id)},
            )
            return bool(result.scalar_one())
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar la vigencia de la suscripcion.") from exc

    def get_subscriber_summary(self, person_id: UUID) -> dict | None:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT
                        p.id,
                        p.dni,
                        p.first_names,
                        p.last_names,
                        p.email,
                        p.phone,
                        p.must_change_password,
                        pay.amount,
                        pay.payment_date,
                        pay.valid_from,
                        pay.valid_until,
                        pay.status
                    FROM uce.core_persons p
                    LEFT JOIN LATERAL (
                        SELECT amount, payment_date, valid_from, valid_until, status
                        FROM uce.payments
                        WHERE person_id = p.id
                        ORDER BY created_date DESC, payment_date DESC
                        LIMIT 1
                    ) pay ON true
                    WHERE p.id = :person_id
                    LIMIT 1
                    """
                ),
                {"person_id": str(person_id)},
            )
            row = result.mappings().first()
            return dict(row) if row else None
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al consultar la informacion del suscriptor.") from exc

    def list_subscribers(self) -> list[dict]:
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT
                        p.id,
                        p.dni,
                        p.first_names,
                        p.last_names,
                        p.email,
                        p.phone,
                        p.is_active,
                        pay.amount,
                        pay.payment_date,
                        pay.valid_from,
                        pay.valid_until,
                        pay.status
                    FROM uce.core_persons p
                    LEFT JOIN LATERAL (
                        SELECT amount, payment_date, valid_from, valid_until, status
                        FROM uce.payments
                        WHERE person_id = p.id
                        ORDER BY created_date DESC, payment_date DESC
                        LIMIT 1
                    ) pay ON true
                    WHERE p.person_type = 'SUSCRIPTOR'
                    ORDER BY p.created_date DESC
                    """
                )
            )
            return [dict(row) for row in result.mappings().all()]
        except SQLAlchemyError as exc:
            raise RepositoryError("Error al listar los suscriptores.") from exc
