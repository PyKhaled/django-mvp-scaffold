document.addEventListener("DOMContentLoaded", function () {
  const element = document.getElementById("swagger-ui");

  if (!element) {
    return;
  }

  SwaggerUIBundle({
    url: "../openapi.json",
    dom_id: "#swagger-ui",
    deepLinking: true,
    displayRequestDuration: true,
    filter: true,
    tryItOutEnabled: true
  });
});
