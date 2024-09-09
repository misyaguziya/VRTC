import {
    useSoftwareVersion,
    useMicHostList,
    useSelectedMicHost,
    useMicDeviceList,
    useSelectedMicDevice,
    useSpeakerDeviceList,
    useSelectedSpeakerDevice,

    useEnableAutoClearMessageBox,
    useSendMessageButtonType,
    useMicThreshold,
    useSpeakerThreshold,
} from "@store";

import { useStdoutToPython } from "./useStdoutToPython";

import { arrayToObject } from "@utils/arrayToObject";

export const useConfig = () => {
    const { asyncStdoutToPython } = useStdoutToPython();

    const { updateSoftwareVersion } = useSoftwareVersion();
    const { updateMicHostList } = useMicHostList();
    const { updateSelectedMicHost } = useSelectedMicHost();
    const { updateMicDeviceList } = useMicDeviceList();
    const { updateSelectedMicDevice } = useSelectedMicDevice();
    const { updateSpeakerDeviceList } = useSpeakerDeviceList();
    const { updateSelectedSpeakerDevice } = useSelectedSpeakerDevice();
    const { currentEnableAutoClearMessageBox, updateEnableAutoClearMessageBox } = useEnableAutoClearMessageBox();
    const { currentSendMessageButtonType, updateSendMessageButtonType } = useSendMessageButtonType();
    const { currentMicThreshold, updateMicThreshold } = useMicThreshold();
    const { currentSpeakerThreshold, updateSpeakerThreshold } = useSpeakerThreshold();


    const asyncPending = () => new Promise(() => {});
    return {
        getSoftwareVersion: () => {
            updateSoftwareVersion(asyncPending);
            asyncStdoutToPython("/config/version");
        },
        updateSoftwareVersion: (payload) => updateSoftwareVersion(payload.data),

        // Device
        getMicHostList: () => {
            updateMicHostList(asyncPending);
            asyncStdoutToPython("/controller/list_mic_host");
        },
        updateMicHostList: (payload) => {
            updateMicHostList(arrayToObject(payload.data));
        },
        getSelectedMicHost: () => {
            updateSelectedMicHost(asyncPending);
            asyncStdoutToPython("/config/choice_mic_host");
        },
        updateSelectedMicHost: (payload) => {
            updateSelectedMicHost(payload.data);
        },
        setSelectedMicHost: (selected_mic_host) => {
            updateSelectedMicHost(asyncPending);
            asyncStdoutToPython("/controller/callback_set_mic_host", selected_mic_host);
        },

        getMicDeviceList: () => {
            updateMicDeviceList(asyncPending);
            asyncStdoutToPython("/controller/list_mic_device");
        },
        updateMicDeviceList: (payload) => {
            updateMicDeviceList(arrayToObject(payload.data));
        },
        getSelectedMicDevice: () => {
            updateSelectedMicDevice(asyncPending);
            asyncStdoutToPython("/config/choice_mic_device");
        },
        updateSelectedMicDevice: (payload) => {
            updateSelectedMicDevice(payload.data);
        },
        setSelectedMicDevice: (selected_mic_device) => {
            updateSelectedMicDevice(asyncPending);
            asyncStdoutToPython("/controller/callback_set_mic_device", selected_mic_device);
        },

        getSpeakerDeviceList: () => {
            updateSpeakerDeviceList(asyncPending);
            asyncStdoutToPython("/controller/list_speaker_device");
        },
        updateSpeakerDeviceList: (payload) => {
            updateSpeakerDeviceList(arrayToObject(payload.data));
        },
        getSelectedSpeakerDevice: () => {
            updateSelectedSpeakerDevice(asyncPending);
            asyncStdoutToPython("/config/choice_speaker_device");
        },
        updateSelectedSpeakerDevice: (payload) => {
            updateSelectedSpeakerDevice(payload.data);
        },
        setSelectedSpeakerDevice: (selected_speaker_device) => {
            updateSelectedSpeakerDevice(asyncPending);
            asyncStdoutToPython("/controller/callback_set_speaker_device", selected_speaker_device);
        },

        updateMicHostAndDevice: (payload) => {
            updateSelectedMicHost(payload.data.host);
            updateSelectedMicDevice(payload.data.device);
        },

        getMicThreshold: () => {
            // updateMicThreshold(asyncPending);
            asyncStdoutToPython("/config/input_mic_energy_threshold");
        },
        setMicThreshold: (mic_threshold) => {
            // updateMicThreshold(asyncPending);
            asyncStdoutToPython("/controller/callback_set_mic_energy_threshold", mic_threshold);
        },
        currentMicThreshold: currentMicThreshold,
        updateMicThreshold: (payload) => {
            updateMicThreshold(payload.data);
        },

        getSpeakerThreshold: () => {
            // updateSpeakerThreshold(asyncPending);
            asyncStdoutToPython("/config/input_speaker_energy_threshold");
        },
        setSpeakerThreshold: (speaker_threshold) => {
            // updateSpeakerThreshold(asyncPending);
            asyncStdoutToPython("/controller/callback_set_speaker_energy_threshold", speaker_threshold);
        },
        currentSpeakerThreshold: currentSpeakerThreshold,
        updateSpeakerThreshold: (payload) => {
            updateSpeakerThreshold(payload.data);
        },



        // Others
        getEnableAutoClearMessageBox: () => {
            updateEnableAutoClearMessageBox(asyncPending);
            asyncStdoutToPython("/config/enable_auto_clear_message_box");
        },
        toggleEnableAutoClearMessageBox: () => {
            updateEnableAutoClearMessageBox(asyncPending);
            if (currentEnableAutoClearMessageBox.data) {
                asyncStdoutToPython("/controller/callback_disable_auto_clear_chatbox");
            } else {
                asyncStdoutToPython("/controller/callback_enable_auto_clear_chatbox");
            }
        },
        currentEnableAutoClearMessageBox: currentEnableAutoClearMessageBox,
        updateEnableAutoClearMessageBox: (payload) => {
            updateEnableAutoClearMessageBox(payload.data);
        },

        getSendMessageButtonType: () => {
            updateSendMessageButtonType(asyncPending);
            asyncStdoutToPython("/config/send_message_button_type");
        },
        setSendMessageButtonType: (selected_type) => {
            updateSendMessageButtonType(asyncPending);
            asyncStdoutToPython("/controller/callback_set_send_message_button_type", selected_type);
        },
        currentSendMessageButtonType: currentSendMessageButtonType,
        updateSendMessageButtonType: (payload) => {
            updateSendMessageButtonType(payload.data);
        },



    };
};