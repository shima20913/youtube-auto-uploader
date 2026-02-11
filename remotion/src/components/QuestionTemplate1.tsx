import React from 'react';
import {
    AbsoluteFill,
    spring,
    useCurrentFrame,
    useVideoConfig,
    interpolate,
} from 'remotion';
import { QuestionData } from '../themes/daily-themes';
import { getDailyTheme } from '../themes/daily-themes';

export const QuestionTemplate1: React.FC<{ data: QuestionData }> = ({ data }) => {
    const frame = useCurrentFrame();
    const { fps, width, height } = useVideoConfig();
    const theme = getDailyTheme();

    // アニメーション
    const titleProgress = spring({
        frame,
        fps,
        config: {
            damping: 100,
            stiffness: 200,
        },
    });

    const titleY = interpolate(titleProgress, [0, 1], [-100, 0]);
    const titleOpacity = interpolate(titleProgress, [0, 1], [0, 1]);

    const optionsProgress = spring({
        frame: frame - 20,
        fps,
        config: {
            damping: 100,
            stiffness: 200,
        },
    });

    return (
        <AbsoluteFill
            style={{
                backgroundColor: theme.backgroundColor,
                justifyContent: 'center',
                alignItems: 'center',
                fontFamily: 'sans-serif',
            }}
        >
            {/* Question Title */}
            <div
                style={{
                    position: 'absolute',
                    top: height * 0.2 + titleY,
                    opacity: titleOpacity,
                    width: width * 0.9,
                    textAlign: 'center',
                }}
            >
                <h1
                    style={{
                        fontSize: 80,
                        color: theme.primaryColor,
                        fontWeight: 'bold',
                        margin: 0,
                        padding: '0 20px',
                        lineHeight: 1.2,
                    }}
                >
                    {data.question}
                </h1>
            </div>

            {/* Options */}
            <div
                style={{
                    position: 'absolute',
                    top: height * 0.5,
                    width: width * 0.85,
                    opacity: optionsProgress,
                }}
            >
                {data.options.map((option, index) => {
                    const optionDelay = spring({
                        frame: frame - (30 + index * 10),
                        fps,
                        config: {
                            damping: 100,
                            stiffness: 200,
                        },
                    });

                    const optionX = interpolate(optionDelay, [0, 1], [width, 0]);

                    return (
                        <div
                            key={index}
                            style={{
                                transform: `translateX(${optionX}px)`,
                                backgroundColor: theme.accentColor,
                                color: theme.textColor,
                                padding: '25px 30px',
                                margin: '15px 0',
                                borderRadius: 15,
                                fontSize: 50,
                                fontWeight: 600,
                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                            }}
                        >
                            {String.fromCharCode(65 + index)}. {option}
                        </div>
                    );
                })}
            </div>
        </AbsoluteFill>
    );
};
