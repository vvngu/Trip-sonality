const API_URL = "http://localhost:8000/plan_trip";

function getInput(id: string): string {
  return (document.getElementById(id) as HTMLInputElement).value.trim();
}

async function sendRequest() {
  const destination = getInput("destination");
  const mbti = (document.getElementById("mbti") as HTMLSelectElement).value;
  const interests = getInput("interests")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  const dislikes = getInput("dislikes")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const payload = {
    destination,
    mbti,
    interests,
    dislikes,
  };

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    const result = JSON.stringify(data, null, 2);
    (document.getElementById("result") as HTMLPreElement).textContent = result;
  } catch (err) {
    console.error(err);
    (document.getElementById("result") as HTMLPreElement).textContent =
      "❌ Failed to fetch trip plan.";
  }
}

// ⬇️ 将函数挂到 window 供 HTML 按钮调用
(window as any).sendRequest = sendRequest;
