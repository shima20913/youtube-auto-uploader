import React from 'react';
import { Composition } from 'remotion';
import { QuestionTemplate1 } from './components/QuestionTemplate1';
import { QuizWithVideos } from './components/QuizWithVideos';

export const RemotionRoot: React.FC = () => {
    return (
        <>
            <Composition
                id="QuestionTemplate1"
                component={QuestionTemplate1}
                durationInFrames={150}
                fps={30}
                width={1080}
                height={1920}
                defaultProps={{
                    data: {
                        id: 'test-1',
                        question: 'あなたはどっち派？',
                        options: ['朝型人間', '夜型人間'],
                    },
                }}
            />

            <Composition
                id="QuizWithVideos"
                component={QuizWithVideos}
                durationInFrames={1050} // 8秒×4選択肢 + 3秒 = 35秒
                fps={30}
                width={1080}
                height={1920}
                defaultProps={{
                    data: {
                        question: '一週間過ごすなら？',
                        questionEn: 'Where would you spend a week?',
                        choices: [
                            { number: 1, text: '溶岩の中', textEn: 'In the lava', videoPath: 'videos/lava.mp4' },
                            { number: 2, text: '氷の部屋', textEn: 'Ice room', videoPath: 'videos/ice.mp4' },
                            { number: 3, text: '宇宙空間', textEn: 'Outer space', videoPath: 'videos/space.mp4' },
                            { number: 4, text: '水中都市', textEn: 'Underwater city', videoPath: 'videos/underwater.mp4' },
                        ],
                        endMessage: 'あなたはどこに住みたいと思いましたか？\n感想はコメント欄へ！',
                        endMessageEn: 'Where would you like to live?\nComment below!',
                    },
                }}
            />
        </>
    );
};
