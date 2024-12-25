import styles from "./Supporters.module.scss";
import clsx from "clsx";
import { useTranslation } from "react-i18next";

const supporter_images = import.meta.glob("@images/supporters/supporters_images/*.{png,jpg,jpeg,svg}", { eager: true });
const chato_expression_images = import.meta.glob("@images/supporters/chato_expressions/*.{png,jpg,jpeg,svg}", { eager: true });
import fanbox_img from "@images/supporters/c_fanbox_1620x580.png";
import vrct_supporters_title from "@images/supporters/vrct_supporters_title.png";
import fanbox_button from "@images/supporters/fanbox_button.png";
import kofi_preparing from "@images/supporters/kofi_preparing.png";

const mogu_count = 8;
const mochi_count = 3;
const fuwa_count = 4;
const basic_count = 5;
const former_count = 2;
const default_icon_numbers = ["05", "06", "07", "11"];

const supporters_filenames = Array.from({ length: 22 }, (_, index) => `supporter_${String(index + 1).padStart(2, "0")}`);
const chato_expressions_filenames = Array.from({ length: 7 }, (_, index) => `chato_expression_${String(index + 1).padStart(2, "0")}`);

const shuffleArray = (array) => {
    return array
        .map((value) => ({ value, sort: Math.random() }))
        .sort((a, b) => a.sort - b.sort)
        .map(({ value }) => value);
};

const getCategoryImages = (start, count) => {
    const category_images = supporters_filenames.slice(start, start + count);
    return shuffleArray(category_images);
};

const mogu_images = getCategoryImages(0, mogu_count);
const mochi_images = getCategoryImages(mogu_count, mochi_count);
const fuwa_images = getCategoryImages(mogu_count + mochi_count, fuwa_count);
const basic_images = getCategoryImages(mogu_count + mochi_count + fuwa_count, basic_count);
const former_images = getCategoryImages(mogu_count + mochi_count + fuwa_count + basic_count, former_count);

const getRandomImage = (images) => {
    const random_index = Math.floor(Math.random() * images.length);
    return images[random_index];
};

const getSupportersImageByFileName = (file_name) => {
    const image_path = Object.keys(supporter_images).find((path) => path.endsWith(file_name + ".png"));
    return image_path ? supporter_images[image_path]?.default : null;
};

const getChatoImageByFileName = (file_name) => {
    const image_path = Object.keys(chato_expression_images).find((path) => path.endsWith(file_name + ".png"));
    return image_path ? chato_expression_images[image_path]?.default : null;
};

const getRandomDelay = (min, max) => {
    const random_value = Math.random() * (max - min) + min;
    return `${random_value.toFixed(1)}s`;
};

export const Supporters = () => {
    return (
        <div className={styles.container}>
            <SupportUsContainer />
            <SupportersContainer />
        </div>
    );
};

const SupportUsContainer = () => {
    return (
        <div className={styles.support_us_container}>
            <img className={styles.fanbox_img} src={fanbox_img} />
            <div className={styles.support_us_button_wrapper}>
                <div className={styles.fanbox_wrapper}>
                <a className={styles.fanbox_button} href="https://vrct-dev.fanbox.cc/" target="_blank" rel="noreferrer" >
                    {/* for adjust size to their parent component's width. */}
                    <img style={ {height: "100%", width: "100%", "objectFit": "contain" }} src={fanbox_button} />
                </a>
                    <p className={styles.mainly_japanese}>日本語 / Mainly Japanese</p>
                </div>
                <div className={styles.kofi_wrapper}>
                    <img className={styles.kofi_preparing} src={kofi_preparing} />
                    <p className={styles.mainly_english}>Mainly English</p>
                </div>
            </div>
        </div>
    );
};

export const SupportersContainer = () => {
    const renderImages = (image_list, class_name) => {
        return image_list.map((file_name) => {
            const img_src = getSupportersImageByFileName(file_name);
            const is_default_icon = default_icon_numbers.some((default_num) => file_name.endsWith(default_num));
            const chato_expression_src = is_default_icon
                ? getChatoImageByFileName(getRandomImage(chato_expressions_filenames))
                : null;
            const random_delay = getRandomDelay(0.1, 6);

            return img_src ? (
                <div
                    key={file_name}
                    className={clsx(styles.supporter_image_wrapper, class_name)}
                    style={{ "--delay": random_delay }}
                >
                    <img className={styles.supporter_image} src={img_src} />
                    {chato_expression_src && (
                        <img
                            className={styles.default_chato_expression_image}
                            src={chato_expression_src}
                        />
                    )}
                </div>
            ) : null;
        });
    };

    return (
        <div className={styles.supporters_container}>
            <img className={styles.vrct_supporters_title} src={vrct_supporters_title} />
            <p className={styles.vrct_supporters_desc}>{`VRCT3.0のアップデートに向けて、むちゃ大変な開発を支えてくれた "Early Supporters" です。\nThey are the 'Early Supporters' who supported us through the incredibly challenging development toward the VRCT3.0 update.`}</p>
            <div className={styles.supporters_wrapper}>
                {renderImages(mogu_images, `${styles.mogu_image}`)}
                {renderImages(mochi_images)}
                {renderImages(fuwa_images)}
                {renderImages(basic_images)}
                {renderImages(former_images)}
            </div>
        </div>
    );
};
