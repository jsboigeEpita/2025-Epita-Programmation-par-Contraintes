import Cookies from 'js-cookie';

export const ensureSessionId = (): string => {
    let sessionId = Cookies.get('SessionId');
	console.log("SessionId from cookie:", sessionId);
    if (!sessionId) {
        sessionId = Math.random().toString(36).substring(2);
        Cookies.set('SessionId', sessionId, {
            expires: 7,
            sameSite: 'Lax',
            secure: true,
        });
    }
    return sessionId;
};
