# Artemis as a custom GPT (ChatGPT)

Anyone with a ChatGPT account can *use* a shared GPT from a link. *Creating* one needs a paid plan.

## Create it
1. Open https://chatgpt.com/gpts/editor and switch to the **Configure** tab.
2. **Name:** Artemis — job-hunting partner
3. **Description:** Finds roles that fit you, scores them honestly, and tailors your resume without inventing anything.
4. **Instructions:** paste all of `INSTRUCTIONS.md` (it's under the 8,000-character limit).
5. **Conversation starters:**
   - artemis setup
   - Try the demo first
   - Is this job a fit for me? (paste a link)
   - Tailor my resume for this job
6. **Knowledge:** upload `artemis-playbooks.md`, `artemis-templates.md` and `artemis-demo-sam-rivera.md`.
7. **Capabilities:** turn on Web Search, Canvas and Code Interpreter & Data Analysis (it creates the
   .docx files). Image generation can stay off.
8. **Create → Share:** choose "Anyone with the link" (or the GPT Store), and copy the link.

## Use it
Open the GPT, say `artemis setup`, and attach your CV (PDF or Word), paste your LinkedIn link, or
paste your whole LinkedIn profile. The GPT doesn't keep your files between chats: keep the four files
it gives you, and attach them at the start of each new chat. Inside a ChatGPT Project, you can add
them to the Project's files once instead.
