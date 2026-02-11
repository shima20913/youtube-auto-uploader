import React, { useEffect, useState } from 'react';
import {
    AbsoluteFill,
    Sequence,
    continueRender,
    delayRender,
    spring,
    useCurrentFrame,
    useVideoConfig,
    interpolate,
    staticFile,
} from 'remotion';
import { getDailyTheme } from '../themes/daily-themes';

const FONT_FAMILY = 'NotoSansCJK, sans-serif';

interface Choice {
    number: number;
    text: string;
    textEn: string; // 英語版
    videoPath: string; // Sora2で生成した横型動画
}

interface QuizData {
    question: string; // 日本語 例: "一週間過ごすなら？"
    questionEn: string; // 英語 例: "Where would you spend a week?"
    choices: Choice[];
    endMessage: string;
    endMessageEn: string;
}

export const QuizWithVideos: React.FC<{ data: QuizData }> = ({ data }) => {
    const { fps, width, height } = useVideoConfig();
    const theme = getDailyTheme();
    const frame = useCurrentFrame();

    // フォントをロードしてからレンダリング開始
    const [handle] = useState(() => delayRender('Loading Japanese font'));
    useEffect(() => {
        const font = new FontFace(
            'NotoSansCJK',
            `url(${staticFile('fonts/NotoSansCJKjp-Bold.otf')})`
        );
        font.load()
            .then((loaded) => {
                (document.fonts as any).add(loaded);
                continueRender(handle);
            })
            .catch(() => continueRender(handle));
    }, [handle]);

    const SCENE_DURATION = 240; // 8秒 (30fps * 8) - Sora2動画の長さに合わせる
    const END_DURATION = 90; // 3秒

    // タイトルアニメーション（最初のシーンのみ）
    const titleOpacity = spring({
        frame,
        fps,
        config: { damping: 100, stiffness: 200 },
    });

    return (
        <AbsoluteFill style={{ backgroundColor: '#000000' }}>
            {/* タイトル（全シーン共通・常に表示） */}
            <div
                style={{
                    position: 'absolute',
                    top: height * 0.08,
                    width: '100%',
                    display: 'flex',
                    justifyContent: 'center',
                    opacity: titleOpacity,
                    zIndex: 100, // 前面に表示
                }}
            >
                <div
                    style={{
                        backgroundColor: theme.primaryColor,
                        padding: '20px 35px',
                        borderRadius: 15,
                        maxWidth: width * 0.9,
                    }}
                >
                    <div style={{
                        fontSize: 90,
                        color: '#FFFFFF',
                        fontWeight: 'bold',
                        lineHeight: 1.2,
                        textAlign: 'center',
                        fontFamily: FONT_FAMILY,
                    }}>
                        {data.question}
                    </div>
                    <div style={{
                        fontSize: 48,
                        color: '#FFFFFF',
                        fontWeight: '600',
                        marginTop: 8,
                        textAlign: 'center',
                        opacity: 0.9,
                        fontFamily: FONT_FAMILY,
                    }}>
                        {data.questionEn}
                    </div>
                </div>
            </div>

            {/* 各選択肢のシーン */}
            {data.choices.map((choice, index) => (
                <Sequence
                    key={index}
                    from={index * SCENE_DURATION}
                    durationInFrames={SCENE_DURATION}
                >
                    <ChoiceScene
                        choice={choice}
                        theme={theme}
                        width={width}
                        height={height}
                        fps={fps}
                    />
                </Sequence>
            ))}

            {/* 最終メッセージ */}
            <Sequence
                from={data.choices.length * SCENE_DURATION}
                durationInFrames={END_DURATION}
            >
                <EndScene message={data.endMessage} theme={theme} />
            </Sequence>
        </AbsoluteFill>
    );
};

// 各選択肢のシーン（タイトルなし）
const ChoiceScene: React.FC<{
    choice: Choice;
    theme: any;
    width: number;
    height: number;
    fps: number;
}> = ({ choice, theme, width, height, fps }) => {
    const frame = useCurrentFrame();

    // 数字を丸数字に変換
    const getCircledNumber = (num: number): string => {
        const circledNumbers = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨'];
        return circledNumbers[num - 1] || num.toString();
    };

    // 選択肢アニメーション
    const choiceProgress = spring({
        frame: frame - 30,
        fps,
        config: { damping: 100, stiffness: 200 },
    });

    const choiceY = interpolate(choiceProgress, [0, 1], [50, 0]);

    // 横型動画のサイズ（16:9）- 画面幅いっぱいに表示
    const videoWidth = width * 1.0; // 100%（隙間なし）
    const videoHeight = (videoWidth * 9) / 16;

    return (
        <AbsoluteFill style={{ backgroundColor: '#000000' }}>
            {/* 横型AI動画の代わりにカラープレースホルダー（テスト用） */}
            <div
                style={{
                    position: 'absolute',
                    top: height * 0.35, // 0.25 → 0.35 下に移動（動画と選択肢を近づける）
                    left: 0, // 左右の隙間をなくす
                    width: videoWidth,
                    height: videoHeight,
                    // アニメーション削除（即時表示）
                    borderRadius: 0, // 角丸もなくす
                    overflow: 'hidden',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.6)',
                    backgroundColor: theme.backgroundColor,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                }}
            >
                <div style={{
                    fontSize: 120,
                    fontWeight: 'bold',
                    color: theme.primaryColor,
                    textAlign: 'center',
                }}>
                    {choice.text}
                </div>
            </div>

            {/* 選択肢テキスト（バイリンガル） */}
            <div
                style={{
                    position: 'absolute',
                    bottom: height * 0.05,
                    width: '100%',
                    textAlign: 'center',
                    transform: `translateY(${choiceY}px)`,
                    opacity: choiceProgress,
                }}
            >
                <div style={{
                    display: 'inline-flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}>
                    <div style={{
                        fontSize: 80,
                        fontWeight: 'bold',
                        color: '#FFFFFF',
                        textShadow: '2px 2px 8px rgba(0,0,0,0.8)',
                        fontFamily: FONT_FAMILY,
                    }}>
                        {getCircledNumber(choice.number)} {choice.text}
                    </div>
                    <div style={{
                        fontSize: 48,
                        fontWeight: '600',
                        color: '#FFFFFF',
                        marginTop: 8,
                        textShadow: '2px 2px 8px rgba(0,0,0,0.8)',
                        opacity: 0.9,
                        fontFamily: FONT_FAMILY,
                    }}>
                        {getCircledNumber(choice.number)} {choice.textEn}
                    </div>
                </div>
            </div>
        </AbsoluteFill>
    );
};

// 最終メッセージシーン
const EndScene: React.FC<{ message: string; theme: any }> = ({ message, theme }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    const opacity = spring({
        frame,
        fps,
        config: { damping: 100, stiffness: 200 },
    });

    const scale = interpolate(opacity, [0, 1], [0.8, 1]);

    return (
        <AbsoluteFill
            style={{
                backgroundColor: '#000000',
                justifyContent: 'center',
                alignItems: 'center',
            }}
        >
            <div
                style={{
                    transform: `scale(${scale})`,
                    opacity,
                    textAlign: 'center',
                    padding: '0 60px',
                }}
            >
                <h1
                    style={{
                        fontSize: 65,
                        color: theme.primaryColor,
                        fontWeight: 'bold',
                        lineHeight: 1.4,
                        textShadow: '2px 2px 8px rgba(0,0,0,0.8)',
                        fontFamily: FONT_FAMILY,
                    }}
                >
                    {message}
                </h1>
            </div>
        </AbsoluteFill>
    );
};
