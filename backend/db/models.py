# -----------------------
# IMPORTS
# -----------------------

# Activa las anotaciones futuras
from __future__ import annotations

# Clases relacionadas para el mapeado de las tablas
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr
from sqlalchemy import Text, ForeignKey, UniqueConstraint, Index, text, BigInteger, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM as PGEnum

# Utilidades
import uuid
from typing import Optional, List, Protocol
from datetime import datetime

# ---------------------------
# Base declarativa
# ---------------------------
class Base(DeclarativeBase):
    pass

# ---------------------------
# Entidades principales
# ---------------------------

# ---------------------------
# CLases de soporte
# ---------------------------
class HasTablename(Protocol):
    __tablename__: str

class UUIDMixin:
    @declared_attr
    def id(cls: type[HasTablename]) -> Mapped[uuid.UUID]:
        return mapped_column(
            f"id_{cls.__tablename__}",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_uuid()")
        )

class CreateTimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),   
        nullable=False,
    )
    
class UpdateTimestampMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
class Persona(Base, UUIDMixin):
    __tablename__ = "persona"
    externals: Mapped[List[External]] = relationship(back_populates="persona", cascade="all, delete-orphan")
    colaboradores: Mapped[List[Colaborador]] = relationship(back_populates="persona", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Persona id={self.id}>"
    
# ---------------------------
# Soporte de identidades externas
# ---------------------------

class External(Base, UUIDMixin, CreateTimestampMixin):
    __tablename__ = "external"
    __table_args__ = (
        UniqueConstraint("provider", "id_provider", name="uq_external_provider"),
        Index("idx_external_correo", "correo"),
        Index("idx_external_provider", "provider", "id_provider"),
    )

    id_persona: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persona.id_persona", ondelete="RESTRICT"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(Text, nullable=False)      # ej: "google"
    id_provider: Mapped[str] = mapped_column(Text, nullable=False)    # el "sub" del id_token
    correo: Mapped[Optional[str]] = mapped_column(Text)
    nombre: Mapped[Optional[str]] = mapped_column(Text)
    hd: Mapped[Optional[str]] = mapped_column(Text)                   # dominio org (si viene)
    persona: Mapped[Persona] = relationship(back_populates="externals")

    def __repr__(self) -> str:
        return f"<External provider={self.provider!r} id_provider={self.id_provider!r} persona={self.id_persona}>"

# ---------------------------
# Vínculos persona/cliente
# ---------------------------

class Cliente(Base, UUIDMixin):
    __tablename__ = "cliente"
    nombre: Mapped[str] = mapped_column(Text, nullable=False)

    dominios: Mapped[List["ClienteDominio"]] = relationship(back_populates="cliente", cascade="all, delete-orphan")
    colaboradores: Mapped[List["Colaborador"]] = relationship(back_populates="cliente", cascade="all, delete-orphan")
    cliente_servicios: Mapped[List["ClienteServicio"]] = relationship(  # ← AÑADIR
        back_populates="cliente", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Cliente id={self.id} nombre={self.nombre!r}>"

class Servicio(Base, UUIDMixin):
    __tablename__ = "servicio"
    nombre: Mapped[str] = mapped_column(Text, nullable=False)

    cliente_servicios: Mapped[List["ClienteServicio"]] = relationship(
        back_populates="servicio", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Servicio id={self.id} nombre={self.nombre!r}>"

class Colaborador(Base, UUIDMixin):
    __tablename__ = "colaborador"
    __table_args__ = (
        Index("idx_colaborador_cliente", "id_cliente"),
        Index("idx_colaborador_persona", "id_persona"),
    )
    id_persona: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("persona.id_persona", ondelete="RESTRICT"), nullable=False
    )
    id_cliente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cliente.id_cliente", ondelete="RESTRICT"), nullable=False
    )
    persona: Mapped["Persona"] = relationship(back_populates="colaboradores")
    cliente: Mapped["Cliente"] = relationship(back_populates="colaboradores")
    tickets: Mapped[List["Ticket"]] = relationship( back_populates="colaborador")
    def __repr__(self) -> str:
        return f"<Colaborador id={self.id} persona={self.id_persona} cliente={self.id_cliente}>"

class Analista(Base, UUIDMixin):
    __tablename__ = "analista"
    id_persona: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("persona.id_persona", ondelete="RESTRICT"), nullable=False
    )
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="analista")  # ← AÑADIR
    persona: Mapped["Persona"] = relationship()
    escalados_solicitados: Mapped[List["Escalado"]] = relationship(            # ← AÑADIR
        back_populates="analista_solicitante",
        foreign_keys="Escalado.id_analista_solicitante",
        cascade="all, delete-orphan",
    )
    
    escalados_derivados: Mapped[List["Escalado"]] = relationship(              # ← AÑADIR
        back_populates="analista_derivado",
        foreign_keys="Escalado.id_analista_derivado",
        cascade="all, delete-orphan",
    )

class ClienteDominio(Base):
    __tablename__ = "cliente_dominio"
    __table_args__ = (
        Index("idx_cliente_dominio_cliente", "id_cliente"),
    )
    dominio: Mapped[str] = mapped_column(Text, primary_key=True)  # p.ej. "unmsm.edu.pe"
    id_cliente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cliente.id_cliente", ondelete="RESTRICT"),
        nullable=False,
    )
    cliente: Mapped[Cliente] = relationship(back_populates="dominios")

    def __repr__(self) -> str:
        return f"<ClienteDominio dominio={self.dominio!r} id_cliente={self.id_cliente}>"

class ClienteServicio(Base, UUIDMixin):
    __tablename__ = "cliente_servicio"
    __table_args__ = (
        UniqueConstraint("id_cliente", "id_servicio", name="uq_cliente_servicio"),
    )
    id_cliente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cliente.id_cliente", ondelete="RESTRICT"), nullable=False
    )
    id_servicio: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("servicio.id_servicio", ondelete="RESTRICT"), nullable=False
    )
    cliente: Mapped["Cliente"] = relationship(back_populates="cliente_servicios")
    servicio: Mapped["Servicio"] = relationship(back_populates="cliente_servicios")
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="cliente_servicio")

    def __repr__(self) -> str:
        return f"<ClienteServicio id={self.id} cliente={self.id_cliente} servicio={self.id_servicio}>"

TicketEstadoEnum = PGEnum(
    "aceptado", "cancelado", "en atención", "finalizado",
    name="ticket_estado",
    create_type=False
)
TicketNivelEnum = PGEnum(
    "bajo", "medio", "alto", "crítico",
    name="ticket_nivel",
    create_type=False
)

TicketTipoEnum = PGEnum(
    "incidencia", "solicitud",
    name="ticket_tipo",
    create_type=False
)

class Ticket(Base, CreateTimestampMixin, UpdateTimestampMixin):
    __tablename__ = "ticket"
    __table_args__ = (
        Index("idx_ticket_estado", "estado"),
        Index("idx_ticket_nivel", "nivel"),
        Index("idx_ticket_created_at", "created_at"),
        Index("idx_ticket_updated_at", "updated_at"),
    )
    id_ticket: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    id_colaborador: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colaborador.id_colaborador", ondelete="RESTRICT"), nullable=False
    )
    id_cliente_servicio: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cliente_servicio.id_cliente_servicio", ondelete="RESTRICT"), nullable=False
    )
    id_analista: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analista.id_analista", ondelete="SET NULL")
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    asunto: Mapped[str] = mapped_column(Text, nullable=False)
    nivel: Mapped[str] = mapped_column(TicketNivelEnum, nullable=False)
    estado: Mapped[str] = mapped_column(TicketEstadoEnum, nullable=False, server_default="'aceptado'")
    diagnostico: Mapped[Optional[str]] = mapped_column(Text)
    colaborador: Mapped["Colaborador"] = relationship(back_populates="tickets")
    cliente_servicio: Mapped["ClienteServicio"] = relationship(back_populates="tickets")
    analista: Mapped[Optional["Analista"]] = relationship(back_populates="tickets")
    conversacion: Mapped[Optional["Conversacion"]] = relationship(
        back_populates="ticket", 
        cascade="all, delete-orphan",
        uselist=False  # ← CLAVE para 1:1
    )
    escalados: Mapped[List["Escalado"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    tipo: Mapped[str] = mapped_column(TicketTipoEnum, nullable=False)
    def __repr__(self) -> str:
        return f"<Ticket id={self.id_ticket} estado={self.estado} nivel={self.nivel}>"
    
    # ------------------------------
    # Propiedades de conveniencia
    # ------------------------------
    
    @property
    def cliente_nombre(self) -> str | None:
        return self.cliente_servicio.cliente.nombre if self.cliente_servicio and self.cliente_servicio.cliente else None

    @property
    def servicio_nombre(self) -> str | None:
        return self.cliente_servicio.servicio.nombre if self.cliente_servicio and self.cliente_servicio.servicio else None

    @property
    def colaborador_nombre(self) -> str | None:
        if not self.colaborador or not self.colaborador.persona:
            return None
        externals = self.colaborador.persona.externals
        return externals[0].nombre if externals else None

    @property
    def email(self) -> str | None:
        if not self.colaborador or not self.colaborador.persona:
            return None
        externals = self.colaborador.persona.externals
        return externals[0].correo if externals else None
    
    @property
    def analista_nombre(self) -> str | None:
        if not self.analista or not self.analista.persona:
            return None
        externals = self.analista.persona.externals
        return externals[0].nombre if externals else None

class Conversacion(Base):
    __tablename__ = "conversacion"
    __table_args__ = (Index("idx_conversacion_ticket", "id_ticket"),)
    id_conversacion: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    id_ticket: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ticket.id_ticket", ondelete="CASCADE"), nullable=False
    )
    contenido: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ticket: Mapped["Ticket"] = relationship(back_populates="conversacion")

    def __repr__(self) -> str:
        return f"<Conversacion id={self.id_conversacion} ticket={self.id_ticket}>"

class Escalado(Base, CreateTimestampMixin):
    __tablename__ = "escalado"
    __table_args__ = (
        Index("idx_escalado_ticket", "id_ticket"),
        Index("idx_escalado_created_at", "created_at"),
    )
    id_escalado: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    id_ticket: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ticket.id_ticket", ondelete="CASCADE"), nullable=False
    )
    id_analista_solicitante: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analista.id_analista", ondelete="RESTRICT"), nullable=False
    )
    id_analista_derivado: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analista.id_analista", ondelete="RESTRICT"), nullable=False
    )
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    ticket: Mapped["Ticket"] = relationship(back_populates="escalados")
    analista_solicitante: Mapped["Analista"] = relationship(
        back_populates="escalados_solicitados",
        foreign_keys=[id_analista_solicitante],
    )
    analista_derivado: Mapped["Analista"] = relationship(
        back_populates="escalados_derivados",
        foreign_keys=[id_analista_derivado],
    )

    def __repr__(self) -> str:
        return f"<Escalado id={self.id_escalado} ticket={self.id_ticket}>"
