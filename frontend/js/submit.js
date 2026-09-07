// ⚠️ REPLACE THIS WITH YOUR AWS API ENDPOINT ⚠️
const API_URL =
  "https://qtq2eftuya.execute-api.eu-north-1.amazonaws.com/register";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const role = form.querySelector('input[name="role"]').value;

    // Validation: Parent/Learner Form
    if (role === "Learner_And_Parent") {
      if (!form.learner_sa_id.value && !form.learner_passport.value) {
        alert("Please provide either an SA ID or Passport for the Learner.");
        return;
      }
      if (
        !form.parent_sa_id_number.value &&
        !form.parent_passport_number.value
      ) {
        alert("Please provide either an SA ID or Passport for the Parent.");
        return;
      }
    }

    // Validation: Teacher Form
    if (role === "Teacher") {
      if (!form.sa_id_number.value && !form.passport_number.value) {
        alert("Please provide either an SA ID or Passport.");
        return;
      }
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    const statusDiv = document.getElementById("statusMessage");
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // UI Loading State
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting securely to database...";
    statusDiv.className = "hidden";

    try {

      let retryCount = 0;
      const maxRetries = 3;
      let response;
      do {
        response = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        retryCount++;
      } while (!response.ok && retryCount < maxRetries);
      if (!response.ok) throw new Error("Server rejected the request");

      // Success UI
      statusDiv.innerHTML = "Application successfully submitted!";
      statusDiv.className = "success";
      form.reset();
      window.scrollTo(0, 0);
    } catch (error) {
      console.error("Submission failed:", error);
      statusDiv.textContent =
        "Network error. Please try again or check your connection.";
      statusDiv.className = "error";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit Application";
    }
  });
});
