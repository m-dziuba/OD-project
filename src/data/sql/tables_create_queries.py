from typing import Dict


def get_all_tables_queries() -> Dict[str, str]:
    return {
        "offers": get_offers_query(),
        "additional_features": get_additional_features_query(),
        "furnishing_features": get_furnishing_features_query(),
        "safety_features": get_safety_features_query(),
        "media_features": get_media_features_query(),
        "offer_features": get_offer_features_query(),
        "coordinates": get_coordinates_query(),
        "geo_levels": get_geo_levels_query(),
        "locations": get_locations(),
        "characteristics": get_characteristics_query(),
        "images": get_images_query(),
    }


def get_offers_query() -> str:
    return (
        """
        CREATE TABLE offers
        (
            id                 INT AUTO_INCREMENT PRIMARY KEY,
            url                VARCHAR(45) NOT NULL,
            date_created       DATETIME,
            date_modified      DATETIME,
            description        VARCHAR(1000)
        );
        """
    )


def get_offer_features_query() -> str:
    return (
        """
        CREATE TABLE offer_features
        (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            offer_id      INT NOT NULL,
            additional_id INT NOT NULL,
            safety_id     INT NOT NULL,
            furnishing_id INT NOT NULL,
            media_id      INT NOT NULL,
            FOREIGN KEY (offer_id) REFERENCES offers (id),
            FOREIGN KEY (additional_id) REFERENCES additional_features (id),
            FOREIGN KEY (safety_id) REFERENCES safety_features (id),
            FOREIGN KEY (furnishing_id) REFERENCES furnishing_features (id),
            FOREIGN KEY (media_id) REFERENCES media_features (id)
        );
        """
    )


def get_additional_features_query() -> str:
    return (
        """
        CREATE TABLE additional_features
        (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            two_floors       BOOLEAN NOT NULL,
            elevator         BOOLEAN NOT NULL,
            balcony          BOOLEAN NOT NULL,
            parking_space    BOOLEAN NOT NULL,
            storage          BOOLEAN NOT NULL,
            cellar           BOOLEAN NOT NULL,
            ac               BOOLEAN NOT NULL,
            separate_kitchen BOOLEAN NOT NULL,
            garden           BOOLEAN NOT NULL
        );
        """
    )


def get_safety_features_query() -> str:
    return (
        """
        CREATE TABLE safety_features
        (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            intercom      BOOLEAN NOT NULL,
            monitoring    BOOLEAN NOT NULL,
            doors_windows BOOLEAN NOT NULL,
            closed_area   BOOLEAN NOT NULL,
            alarm         BOOLEAN NOT NULL,
            roller_blinds BOOLEAN NOT NULL
        );
        """
    )


def get_furnishing_features_query() -> str:
    return (
        """
        CREATE TABLE furnishing_features
        (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            furniture       BOOLEAN NOT NULL,
            fridge          BOOLEAN NOT NULL,
            oven            BOOLEAN NOT NULL,
            stove           BOOLEAN NOT NULL,
            washing_machine BOOLEAN NOT NULL,
            dishwasher      BOOLEAN NOT NULL,
            tv              BOOLEAN NOT NULL
        );
        """
    )


def get_media_features_query() -> str:
    return (
        """
        CREATE TABLE media_features
        (
            id       INT AUTO_INCREMENT PRIMARY KEY,
            tv       BOOLEAN NOT NULL,
            internet BOOLEAN NOT NULL,
            phone    BOOLEAN NOT NULL
        );
        """
    )


def get_locations() -> str:
    return (
        """
        CREATE TABLE locations
        (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            offer_id       INT NOT NULL,
            address        VARCHAR(50),
            geo_levels_id   INT,
            FOREIGN KEY (offer_id) REFERENCES offers (id),
            FOREIGN KEY (geo_levels_id) REFERENCES geo_levels (id)
        );
        """
    )


def get_geo_levels_query() -> str:
    return (
        """
        CREATE TABLE geo_levels
        (
        id        INT AUTO_INCREMENT PRIMARY KEY,
        district  VARCHAR(50) NOT NULL,
        city      VARCHAR(50) NOT NULL,
        subregion VARCHAR(50) NOT NULL,
        region    VARCHAR(50) NOT NULL
        );
        """
    )


def get_coordinates_query() -> str:
    return (
        """
        CREATE TABLE coordinates
        (
            id        INT AUTO_INCREMENT PRIMARY KEY,
            offer_id       INT NOT NULL,
            longitude DOUBLE,
            latitude  DOUBLE,
            FOREIGN KEY (offer_id) REFERENCES offers (id),
            UNIQUE (longitude, latitude)
        );
        """
    )


# TODO do todos... IDE doesn't see them for some reason
def get_characteristics_query() -> str:
    return (
        """
        CREATE TABLE characteristics
        (
            id                     INT AUTO_INCREMENT PRIMARY KEY,
            offer_id               INT NOT NULL,
            price                  INT,
            area                   FLOAT,
            price_per_meter        INT,
            no_of_rooms            INT,
            market                 VARCHAR(50),     # TODO change to a mapping
            floor                  INT,
            year_built             YEAR,
            no_of_floors           INT,
            form_of_ownership      VARCHAR(50),     # TODO change to a mapping,
            type_of_building       VARCHAR(50),     # TODO change to a mapping
            heating                VARCHAR(50),     # TODO change to a mapping
            standard_of_completion VARCHAR(50),     # TODO change to a mapping
            type_of_ownership      VARCHAR(50),     # TODO change to a mapping
            windows                VARCHAR(50),     # TODO change to a mapping
            material               VARCHAR(50),     # TODO change to a mapping
            available_from         VARCHAR(50),     # TODO change to a date
            remote_service         TINYINT,
            FOREIGN KEY (offer_id) REFERENCES offers (id)
        );
        """
    )


def get_images_query() -> str:
    return (
        """
        CREATE TABLE images
        (
            image_url VARCHAR(50) NOT NULL,
            offer_id  INT         NOT NULL,
            FOREIGN KEY (offer_id) REFERENCES offers (id),
            PRIMARY KEY (image_url, offer_id)
        );
        """
    )
