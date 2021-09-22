--Fine constraints
ALTER TABLE lab.fine
    ADD CONSTRAINT fk_fv FOREIGN KEY (car_id) REFERENCES lab.car(car_id);
ALTER TABLE lab.fine
    ADD CONSTRAINT fk_fc FOREIGN KEY (camera_id) REFERENCES lab.camera(camera_id);
ALTER TABLE lab.fine
    ADD CONSTRAINT fk_fa FOREIGN KEY (article_id) REFERENCES lab.article(article_id);

--Owner constraints
ALTER TABLE lab.owner
    ADD CONSTRAINT date_owner CHECK ( date_birth >= '1900-01-01'::date AND date_birth <= current_date);
ALTER TABLE lab.owner
    ADD CONSTRAINT passport_owner CHECK ( passport_id >= 1000000000 and passport_id <= 7099999999  );

--Car constraints
ALTER TABLE lab.car
    ADD CONSTRAINT year_car CHECK ( issue_year >= 1900 AND issue_year <= date_part('year', current_date));
ALTER TABLE lab.car
    ADD CONSTRAINT vin_car CHECK ( length(vin) = 17);
ALTER TABLE lab.car
    ADD CONSTRAINT reg_date CHECK ( reg_date >= '1968-01-01'::date AND reg_date <= current_date);
ALTER TABLE lab.car
    ADD CONSTRAINT fk_co FOREIGN KEY (owner_id) REFERENCES lab.owner(owner_id);

--Camera constraints
ALTER TABLE lab.camera
    ADD CONSTRAINT date_cam CHECK ( date_added >= '2000-01-01'::date AND date_added <= current_date);
