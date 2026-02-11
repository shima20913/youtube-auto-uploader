export interface QuestionData {
    id: string;
    question: string;
    options: string[];
    theme?: string;
    font?: string;
}

export interface DailyTheme {
    name: string;
    primaryColor: string;
    accentColor: string;
    backgroundColor: string;
    textColor: string;
}

export const THEMES: { [key: string]: DailyTheme } = {
    monday: {
        name: 'Pop',
        primaryColor: '#FF6B9D',
        accentColor: '#FFD93D',
        backgroundColor: '#FFF5E4',
        textColor: '#2C3E50',
    },
    tuesday: {
        name: 'Retro',
        primaryColor: '#FF6B35',
        accentColor: '#F7B267',
        backgroundColor: '#6A4C93',
        textColor: '#FFFFFF',
    },
    wednesday: {
        name: 'Cool',
        primaryColor: '#4A90E2',
        accentColor: '#9013FE',
        backgroundColor: '#1E3A8A',
        textColor: '#FFFFFF',
    },
    thursday: {
        name: 'Natural',
        primaryColor: '#2ECC71',
        accentColor: '#F39C12',
        backgroundColor: '#ECF0F1',
        textColor: '#2C3E50',
    },
    friday: {
        name: 'Elegant',
        primaryColor: '#000000',
        accentColor: '#FFD700',
        backgroundColor: '#1A1A1A',
        textColor: '#FFFFFF',
    },
    saturday: {
        name: 'Colorful',
        primaryColor: '#E74C3C',
        accentColor: '#3498DB',
        backgroundColor: '#FFFFFF',
        textColor: '#2C3E50',
    },
    sunday: {
        name: 'Simple',
        primaryColor: '#333333',
        accentColor: '#CCCCCC',
        backgroundColor: '#FFFFFF',
        textColor: '#000000',
    },
};

export function getDailyTheme(): DailyTheme {
    const dayOfWeek = new Date().getDay();
    const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    return THEMES[days[dayOfWeek]];
}
