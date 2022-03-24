from typing import Dict


def all_tables(tables: Dict[str, str]):
    offers(tables)

    additional_features(tables)
    furnishing_features(tables)
    safety_features(tables)
    media_features(tables)
    offer_features(tables)

    coordinates(tables)
    geolevels(tables)
    locations(tables)

    characteristics(tables)
    images(tables)


def offers(tables: Dict[str, str]):
    tables["offers"] = (
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


def offer_features(tables: Dict[str, str]):
    tables["offer_features"] = (
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


def additional_features(tables: Dict[str, str]):
    tables["additional_features"] = (
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


def safety_features(tables: Dict[str, str]):
    tables["safety_features"] = (
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


def media_features(tables: Dict[str, str]):
    tables["furnishing_features"] = (
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


def furnishing_features(tables: Dict[str, str]):
    tables["media_features"] = (
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


def locations(tables: Dict[str, str]):
    tables["locations"] = (
        """
        CREATE TABLE locations
        (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            address        VARCHAR(50),
            geolevels_id   INT,
            coordinates_id INT,
            FOREIGN KEY (geolevels_id) REFERENCES geolevels (id),
            FOREIGN KEY (coordinates_id) REFERENCES coordinates (id)
        );
        """
    )


def geolevels(tables: Dict[str, str]):
    tables["geolevels"] = (
        """
        CREATE TABLE geolevels
        (
        id        INT AUTO_INCREMENT PRIMARY KEY,
        district  VARCHAR(50) NOT NULL,
        city      VARCHAR(50) NOT NULL,
        subregion VARCHAR(50) NOT NULL,
        region    VARCHAR(50) NOT NULL
        );
        """
    )


def coordinates(tables: Dict[str, str]):
    tables["coordinates"] = (
        """
        CREATE TABLE coordinates
        (
            id        INT AUTO_INCREMENT PRIMARY KEY,
            longitude DOUBLE,
            latitude  DOUBLE,
            UNIQUE (longitude, latitude)
        );
        """
    )


def characteristics(tables: Dict[str, str]):
    tables["characteristics"] = (
        """
        CREATE TABLE characteristics
        (
            id                     INT AUTO_INCREMENT PRIMARY KEY,
            price                  INT,
            area                   FLOAT,
            price_per_meter        INT,
            no_of_rooms            INT,
            market                 VARCHAR(50), # TODO change to a mapping
            floor                  INT,
            year_built             YEAR,
            no_of_floors           INT,
            form_of_ownership      VARCHAR(50), # TODO change to a mapping,
            type_of_building       VARCHAR(50), # TODO change to a mapping
            heating                VARCHAR(50), # TODO change to a mapping
            standard_of_completion VARCHAR(50), # TODO change to a mapping
            type_of_ownership      VARCHAR(50), # TODO change to a mapping
            windows                VARCHAR(50), # TODO change to a mapping
            material               VARCHAR(50), # TODO change to a mapping
            available_from         VARCHAR(50), # TODO change to a date
            remote_service         TINYINT
        );
        """
    )


def images(tables: Dict[str, str]):
    tables["images"] = (
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
