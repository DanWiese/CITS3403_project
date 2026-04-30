/**
 * Participant Invite Management
 * Handles sharing event links and invitation workflows
 */

async function shareEventInvite() {
    const discussion = document.getElementById('discussion');
    const inviteUrl = discussion.dataset.shareUrl || window.location.href;

    if (navigator.share) {
        try {
            await navigator.share({
                title: 'Join my event on Shindig',
                text: 'Use this link to join the event:',
                url: inviteUrl,
            });
            return;
        } catch (error) {
            // Fall back to clipboard if share is cancelled or unsupported in this context.
        }
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
        try {
            await navigator.clipboard.writeText(inviteUrl);
            alert('Invite link copied. Share it with participants.');
            return;
        } catch (error) {
            // Fall through to prompt fallback.
        }
    }

    prompt('Copy this invite link:', inviteUrl);
}

function closeJoinModal() {
    const joinModal = document.getElementById('joinModal');
    if (joinModal) {
        joinModal.classList.remove('show');
    }
}

async function submitJoinRequest() {
    const discussion = document.getElementById('discussion');
    const token = discussion ? discussion.dataset.inviteToken : '';
    const requestUrl = discussion ? discussion.dataset.requestUrl : '';

    if (!token || !requestUrl) {
        alert('This invite link is missing request details.');
        return;
    }

    try {
        const response = await fetch(requestUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            alert(result.message || 'Unable to send join request.');
            return;
        }

        alert('Request sent to the host. You will be added after approval.');
        closeJoinModal();
    } catch (error) {
        console.error('Failed to send join request:', error);
        alert('Unable to send join request.');
    }
}
