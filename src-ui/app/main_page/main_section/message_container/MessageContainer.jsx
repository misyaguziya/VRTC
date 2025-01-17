import { useResizable } from "react-resizable-layout";
import { useRef, useEffect, useState } from "react";
import styles from "./MessageContainer.module.scss";
import { appWindow } from "@tauri-apps/api/window";
import { LogBox } from "./log_box/LogBox";
import { MessageLogSettingsContainer } from "./message_log_settings_container/MessageLogSettingsContainer";
import { MessageInputBox } from "./message_input_box/MessageInputBox";
import { useMessageInputBoxRatio } from "@logics_main";
import { useUiScaling } from "@logics_configs";
import { useStore_IsAppliedInitMessageBoxHeight } from "@store";

export const MessageContainer = () => {
    const { currentMessageInputBoxRatio, asyncSetMessageInputBoxRatio } = useMessageInputBoxRatio();
    const { currentUiScaling } = useUiScaling();
    const [is_hovered, setIsHovered] = useState(false);
    const [message_box_height_in_rem, setMessageBoxHeightInRem] = useState(10);
    const FONT_SIZE_STANDARD = 10 * currentUiScaling.data / 100; // 10px = 1rem
    const { currentIsAppliedInitMessageBoxHeight, updateIsAppliedInitMessageBoxHeight } = useStore_IsAppliedInitMessageBoxHeight();

    const container_ref = useRef(null);
    const log_box_ref = useRef(null);
    const message_box_wrapper_ref = useRef(null);

    const asyncSetMessageBoxHeightInRem = async (data) => {
        const minimized = await appWindow.isMinimized();
        if (minimized) return; // don't save while the window is minimized.
        setMessageBoxHeightInRem(data);
    };

    const calculateMessageBoxRatioAndHeight = () => {
        if (!currentIsAppliedInitMessageBoxHeight.data) {
            asyncSetMessageInputBoxRatio(currentMessageInputBoxRatio.data);
            asyncSetMessageBoxHeightInRem(convertRatioToRem(currentMessageInputBoxRatio.data));
            return;
        }

        if (log_box_ref.current && message_box_wrapper_ref.current && container_ref.current) {
            const container_height = container_ref.current.offsetHeight;
            const container_padding_bottom = parseFloat(window.getComputedStyle(container_ref.current).paddingBottom);
            const total_height = container_height - container_padding_bottom;

            const message_box_height = message_box_wrapper_ref.current.offsetHeight;
            const message_box_ratio = (message_box_height / total_height) * 100;

            asyncSetMessageInputBoxRatio(message_box_ratio);
            asyncSetMessageBoxHeightInRem(convertRatioToRem(message_box_ratio));
        } else {
            console.warn("References not ready for calculation");
        }
    };

    const { position, separatorProps } = useResizable({
        axis: "y",
        reverse: true,
        onResizeEnd: calculateMessageBoxRatioAndHeight,
    });

    useEffect(() => {
        asyncSetMessageBoxHeightInRem((position / FONT_SIZE_STANDARD) - 1.4);
    }, [position]);

    useEffect(() => {
        asyncSetMessageBoxHeightInRem(convertRatioToRem(currentMessageInputBoxRatio.data));
    }, [currentMessageInputBoxRatio.data]);

    const convertRatioToRem = (ratio) => {
        if (!container_ref.current) return 0;
        const container_height = container_ref.current.offsetHeight;
        const container_padding_bottom = parseFloat(window.getComputedStyle(container_ref.current).paddingBottom);
        const total_height = container_height - container_padding_bottom;
        return total_height === 0 ? 0 : ((ratio / 100) * total_height / FONT_SIZE_STANDARD);
    };

    useEffect(() => {
        calculateMessageBoxRatioAndHeight();
        updateIsAppliedInitMessageBoxHeight(true); // Ensure this happens after initial calculation
    }, []);

    useEffect(() => {
        let resizeTimeout;

        const unlisten = appWindow.onResized(() => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                calculateMessageBoxRatioAndHeight();
            }, 200);
        });

        return () => {
            unlisten.then((dispose) => dispose());
        };
    }, []);

    return (
        <div className={styles.container} ref={container_ref}>
            <div className={styles.log_box_resize_wrapper}
                ref={log_box_ref}
                onMouseOver={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                <LogBox />
                <MessageLogSettingsContainer to_visible_toggle_bar={is_hovered} />
            </div>
            <Separator {...separatorProps} onDragStart={calculateMessageBoxRatioAndHeight} />
            <div
                className={styles.message_box_resize_wrapper}
                ref={message_box_wrapper_ref}
                style={{ height: `${message_box_height_in_rem}rem` }}
            >
                <MessageInputBox />
            </div>
        </div>
    );
};

const Separator = ({ onDragStart, ...props }) => (
    <div tabIndex={0} className={styles.separator} {...props} onDragStart={onDragStart}>
        <span className={styles.separator_line}></span>
    </div>
);
