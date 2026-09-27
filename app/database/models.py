from datetime import datetime
import os

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tracker.db")


class Base(DeclarativeBase):
    pass


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="store",
        cascade="all, delete-orphan",
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id"),
        nullable=False,
    )

    shopify_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    handle: Mapped[str | None] = mapped_column(
        String(500)
    )

    product_url: Mapped[str | None] = mapped_column(
        String(1000)
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    price: Mapped[float | None] = mapped_column(
        Float
    )

    available_sizes: Mapped[str | None] = mapped_column(
        String(1000)
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # Existing primary image field
    image_url: Mapped[str | None] = mapped_column(
        String(1000)
    )

    # Existing local image field
    local_image_path: Mapped[str | None] = mapped_column(
        String(1000)
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    store: Mapped["Store"] = relationship(
        back_populates="products"
    )

    variants: Mapped[list["Variant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.position",
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )

    shopify_id: Mapped[str | None] = mapped_column(
        String(100)
    )

    image_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    product: Mapped["Product"] = relationship(
        back_populates="images"
    )


class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )

    shopify_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(
        String(500)
    )

    size: Mapped[str | None] = mapped_column(
        String(100)
    )

    price: Mapped[float | None] = mapped_column(
        Float
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    product: Mapped["Product"] = relationship(
        back_populates="variants"
    )


engine = create_engine(
    DATABASE_URL,
    echo=False,
)


def init_db():
    Base.metadata.create_all(engine)