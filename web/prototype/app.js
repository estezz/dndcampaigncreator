import React, { useState, useCallback, Fragment } from 'react';
import {
  Wand2,
  Loader2,
  AlertTriangle,
  Gift,
  Shuffle,
  Download,
  BookOpen,
  Eye,
  Map,
  Paperclip,
  X,
  Dices, // Using this for the animation
  Printer,
  Sparkles, // Added for story line generation
} from 'lucide-react';

// --- API & Utility Configuration ---

const GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent";
const IMAGEN_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict";
const API_KEY = ""; // Leave as-is, will be populated by the environment

// The JSON schema for the D&D module
const MODULE_SCHEMA = {
  type: "OBJECT",
  properties: {
    title: { type: "STRING" },
    location: { type: "STRING" },
    setup: {
      type: "STRING",
      description: "HTML formatted setup and background story for the module."
    },
    plotHooks: {
      type: "ARRAY",
      items: {
        type: "OBJECT",
        properties: {
          title: { type: "STRING" },
          description: {
            type: "STRING",
            description: "HTML formatted description of the plot hook."
          }
        },
        required: ["title", "description"]
      }
    },
    mainPlotSteps: {
      type: "ARRAY",
      items: {
        type: "OBJECT",
        properties: {
          title: { type: "STRING" },
          description: {
            type: "STRING",
            description: "HTML formatted description of this plot step."
          },
          imagePrompt: { // Image prompt for each plot step
            type: "STRING",
            description: "A prompt for generating an atmospheric image (16:9) representing this plot step."
          }
        },
        required: ["title", "description", "imagePrompt"] // Added imagePrompt
      }
    },
    mainCharacters: {
      type: "ARRAY",
      items: {
        type: "OBJECT",
        properties: {
          name: { type: "STRING" },
          description: {
            type: "STRING",
            description: "HTML formatted description of the character."
          },
          imagePrompt: {
            type: "STRING",
            description: "A prompt for generating a portrait (1:1) of this character."
          },
          statBlock: {
            type: "STRING",
            description: "HTML formatted stat block. Can be an empty string if not applicable."
          }
        },
        required: ["name", "description", "imagePrompt", "statBlock"]
      }
    },
    monsterStatBlocks: {
      type: "ARRAY",
      items: {
        type: "OBJECT",
        properties: {
          name: { type: "STRING" },
          statBlock: {
            type: "STRING",
            description: "HTML formatted stat block for the monster."
          },
          imagePrompt: {
            type: "STRING",
            description: "A prompt for generating an image (1:1) of this monster."
          }
        },
        required: ["name", "statBlock", "imagePrompt"]
      }
    },
    mapPrompt: {
      type: "STRING",
      description: "A prompt for a top-down, 16:9 battle map."
    },
    regionMapPrompt: {
      type: "STRING",
      description: "A prompt for a top-down, 16:9 region map of the greater area."
    },
    startPointPrompt: {
      type: "STRING",
      description: "A prompt for an atmospheric, 16:9 scene of the starting point."
    },
    rewardsImagePrompt: {
      type: "STRING",
      description: "A prompt for a 16:9 image representing the main rewards."
    },
    rewardsList: {
      type: "ARRAY",
      items: {
        type: "OBJECT",
        properties: {
          name: { type: "STRING" },
          description: {
            type: "STRING",
            description: "HTML formatted description of the reward."
          },
          value: {
            type: "STRING",
            description: "The value of the reward, e.g., '500 gp' or 'Rare'."
          }
        },
        required: ["name", "description", "value"]
      }
    },
    // --- NEW: Integrated Story Tools ---
    generatedMagicItems: {
      type: "ARRAY",
      description: "Generate 3 unique magic items relevant to the module.",
      items: {
        type: "OBJECT",
        properties: {
          name: { type: "STRING" },
          description: {
            type: "STRING",
            description: "HTML formatted description of the magic item."
          },
          value: {
            type: "STRING",
            description: "The value of the item, e.g., '500 gp' or 'Rare'."
          }
        },
        required: ["name", "description", "value"]
      }
    },
    generatedPlotTwists: {
      type: "ARRAY",
      description: "Generate 3 unexpected plot twists relevant to the module.",
      items: {
        type: "OBJECT",
        properties: {
          title: { type: "STRING" },
          description: {
            type: "STRING",
            description: "HTML formatted description of the plot twist."
          }
        },
        required: ["title", "description"]
      }
    }
    // --- End of Integrated Story Tools ---
  },
  required: [
    "title", "location", "setup", "plotHooks", "mainPlotSteps",
    "mainCharacters", "monsterStatBlocks", "mapPrompt",
    "regionMapPrompt", "startPointPrompt", "rewardsImagePrompt",
    "rewardsList",
    "generatedMagicItems", "generatedPlotTwists" // Added to required
  ]
};

/**
 * A resilient fetch wrapper with exponential backoff and timeout.
 * @param {string} url - The URL to fetch.
 * @param {object} options - The fetch options (method, headers, body).
 * @param {number} maxRetries - Maximum number of retries.
 * @param {number} timeout - Timeout in milliseconds.
 * @returns {Promise<object>} - The JSON response.
 */
const resilientFetch = async (url, options, maxRetries = 3, timeout = 60000) => {
  let attempt = 0;
  let delay = 1000;

  while (attempt < maxRetries) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(id);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      if (data.error) {
        throw new Error(`API Error: ${data.error.message}`);
      }
      return data;

    } catch (error) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        throw new Error(`Request timed out after ${timeout / 1000}s`);
      }
      
      console.warn(`Attempt ${attempt + 1} failed: ${error.message}`);
      attempt++;
      if (attempt >= maxRetries) {
        if (error.message && error.message.includes("401")) {
          throw new Error("Authentication failed. Please check your API key.");
        }
        throw error;
      }
      
      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 2; // Exponential backoff
    }
  }
  throw new Error("API request failed after all retries.");
};

// --- API Helper Functions ---

/**
 * Generates simple text using Gemini (for story line).
 * @param {string} prompt - The user's prompt.
 * @returns {Promise<string>} - The generated text.
 */
const generateSimpleText = async (prompt) => {
  const payload = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      temperature: 0.7,
      topK: 40,
    }
  };
  
  const url = `${GEMINI_API_URL}?key=${API_KEY}`;
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  };

  const result = await resilientFetch(url, options);
  
  // --- Start of Fix ---
  // Check for prompt feedback (safety blocking)
  if (result.promptFeedback) {
    const blockReason = result.promptFeedback.blockReason || 'Unknown';
    console.error(`Simple text generation blocked: ${blockReason}`, result);
    throw new Error(`The request was blocked by the API. Reason: ${blockReason}.`);
  }
  // --- End of Fix ---
  
  const text = result.candidates?.[0]?.content?.parts?.[0]?.text;
  
  if (!text) {
    console.error("Invalid response structure from generateSimpleText:", result);
    throw new Error("No text generated by API.");
  }
  return text.trim();
};


/**
 * Generates the structured D&D module text using Gemini.
 * @param {object} formData - The user's form input.
 * @param {Array<object>} inspirationalImages - Array of image objects { mimeType, data }
 * @returns {Promise<object>} - The parsed JSON module data.
 */
const generateModuleText = async (formData, inspirationalImages) => {
  const { storyLine, otherThings, rewards, level, length, creativity, numPlayers } = formData;
  
  const systemPrompt = "You are a creative and detailed Dungeons & Dragons module architect. Your task is to generate a complete, structured module based on the user's inputs. Respond ONLY with the valid JSON object defined by the schema.";
  
  // Logic to map creativity level to descriptive text
  const creativityDescription = creativity === 1 ? "Extremely conventional and traditional. Stick very closely to D&D tropes."
    : creativity <= 3 ? "Conventional with minor twists."
    : creativity <= 7 ? "A good mix of classic tropes and original ideas. Interpret prompts creatively."
    : creativity <= 9 ? "Highly imaginative, unique, and unusual."
    : "Wildly imaginative, subversive, and unexpected. Feel free to reinterpret the prompts in a very creative way.";

  const userPrompt = `
    Please generate a D&D module with the following specifications:
    - Party Size: ${numPlayers} players
    - Character Level: ${level}
    - Story Line: ${storyLine}
    - Other Things to Include: ${otherThings}
    - Rewards to Include: ${rewards} (in addition to the 'generatedMagicItems')
    - Target Length (Hours): ${length}

    **Creativity Interpretation**: The creativity level is set to ${creativity} out of 10. This means the interpretation should be: ${creativityDescription}
    
    **Complexity**: You MUST scale the module's complexity (plot steps, encounters) based on the target length. A ${length}-hour module should have an appropriate number of steps.
    
    ${inspirationalImages.length > 0 ? "**Inspiration Images**: Use the following uploaded images as inspiration for the module's atmosphere, characters, locations, and overall feel." : ""}

    **Formatting**: Ensure all descriptions ('setup', 'description', 'statBlock') are formatted as clean, readable HTML (e.g., using <p>, <ul>, <li>, <strong>).
    
    **Balancing (CRITICAL)**: All monsters, NPC statblocks, and rewards (both quantity and quality in 'rewardsList' and 'generatedMagicItems') MUST be balanced for a party of ${numPlayers} players at level ${level}.

    **Integrated Content**: As part of this single response, you must ALSO generate 3 unique magic items and 3 plot twists relevant to the module, using the 'generatedMagicItems' and 'generatedPlotTwists' properties.
  `;

  const parts = [{ text: userPrompt }];
  inspirationalImages.forEach(img => {
    parts.push({
      inlineData: {
        mimeType: img.mimeType,
        data: img.data
      }
    });
  });

  const payload = {
    contents: [{ parts: parts }],
    systemInstruction: {
      parts: [{ text: systemPrompt }]
    },
    generationConfig: {
      responseMimeType: "application/json",
      responseSchema: MODULE_SCHEMA,
    },
  };

  const url = `${GEMINI_API_URL}?key=${API_KEY}`;
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  };

  const result = await resilientFetch(url, options, 3, 120000); // 2 min timeout for text gen

  try {
    // --- Start of Fix ---
    // Check for prompt feedback (safety blocking)
    if (result.promptFeedback) {
      const blockReason = result.promptFeedback.blockReason || 'Unknown';
      throw new Error(`The request was blocked by the API. Reason: ${blockReason}. Please modify your prompts.`);
    }
    // --- End of Fix ---

    const jsonText = result.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!jsonText) {
      throw new Error("Invalid response structure from Gemini API.");
    }
    return JSON.parse(jsonText);
  } catch (parseError) {
    console.error("Failed to parse JSON response:", parseError, result);
    // Re-throw the specific block error if it exists
    if (parseError.message.startsWith("The request was blocked")) {
      throw parseError;
    }
    // Otherwise, throw the generic parse error
    throw new Error("Failed to parse module data from API. The response may be invalid.");
  }
};

/**
 * Generates a single image using Imagen.
 * @param {string} prompt - The image generation prompt.
 * @param {string} aspectRatio - e.g., "1:1" or "16:9".
 * @returns {Promise<string>} - The base64 data URL of the image.
 */
const generateImage = async (prompt, aspectRatio = "1:1") => {
  const payload = {
    instances: [{ prompt: `d&d fantasy art style, ${prompt}` }],
    parameters: {
      sampleCount: 1,
      aspectRatio: aspectRatio,
    },
  };

  const url = `${IMAGEN_API_URL}?key=${API_KEY}`;
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  };
  
  const result = await resilientFetch(url, options, 3, 180000); // 3 min timeout for image gen

  // Check for prompt feedback (safety blocking) - Imagen format is different
  if (result.error) {
     console.warn(`Image generation failed for prompt: "${prompt}". Reason: ${result.error.message}`);
     throw new Error(result.error.message);
  }

  const base64Data = result.predictions?.[0]?.bytesBase64Encoded;
  if (!base64Data) {
    // Log warning instead of error for individual image failures
    console.warn(`Image generation failed for prompt: "${prompt}"`, result);
    throw new Error("No image data found in Imagen response.");
  }

  return `data:image/png;base64,${base64Data}`;
};

// --- Helper & UI Components ---

const InputLabel = ({ htmlFor, children }) => (
  <label htmlFor={htmlFor} className="block text-sm font-medium text-gray-300 mb-1">
    {children}
  </label>
);

const TextInput = (props) => (
  <input
    {...props}
    className="block w-full bg-gray-800 border-gray-700 text-white rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
  />
);

const TextArea = (props) => (
  <textarea
    {...props}
    className="block w-full bg-gray-800 border-gray-700 text-white rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
  />
);

const IconButton = ({ icon: Icon, text, onClick, loading, className = '', ...props }) => (
  <button
    type="button"
    onClick={onClick}
    disabled={loading}
    className={`w-full flex items-center justify-center gap-2 px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-wait ${className}`}
    {...props}
  >
    {loading ? (
      <Loader2 className="animate-spin h-5 w-5" />
    ) : (
      <Icon className="h-5 w-5" />
    )}
    {text}
  </button>
);

const HtmlRenderer = ({ htmlString }) => (
  <div
    className="prose prose-invert prose-sm md:prose-base max-w-none text-gray-300"
    dangerouslySetInnerHTML={{ __html: htmlString || "<p>Nothing to display.</p>" }}
  />
);

const ImagePlaceholder = ({ loading, imageUrl, alt, aspectRatio = "1:1" }) => {
  const aspectClass = aspectRatio === "16:9" ? "aspect-video" : "aspect-square";
  
  return (
    <div className={`w-full ${aspectClass} bg-gray-800 rounded-lg flex items-center justify-center overflow-hidden border border-gray-700`}>
      {loading && <Loader2 className="h-12 w-12 text-gray-500 animate-spin" />}
      {!loading && imageUrl && (
        <img src={imageUrl} alt={alt} className="w-full h-full object-cover" />
      )}
      {!loading && !imageUrl && (
        <AlertTriangle className="h-12 w-12 text-red-500" />
      )}
    </div>
  );
};

const ErrorDisplay = ({ message }) => (
  <div className="p-4 bg-red-900 border border-red-700 rounded-lg text-red-100 flex items-center gap-3">
    <AlertTriangle className="h-6 w-6 text-red-300" />
    <div>
      <h3 className="font-bold">Generation Failed</h3>
      <p className="text-sm">{message}</p>
    </div>
  </div>
);

const Section = ({ title, icon: Icon, children }) => (
  <section className="mb-8">
    <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2 border-b border-gray-700 pb-2">
      <Icon className="h-6 w-6 text-blue-400" />
      {title}
    </h2>
    {children}
  </section>
);

// --- HTML Generation Functions ---

/**
 * Creates the self-contained HTML file content for download (dark theme).
 * @param {object} moduleData - The generated module JSON.
 * @param {object} images - The object of generated base64 image URLs.
 * @returns {string} - The full HTML document as a string.
 */
const createDownloadHtml = (moduleData, images) => {
  const { title } = moduleData;

  const css = `
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      line-height: 1.6;
      background-color: #1a1a1a;
      color: #e0e0e0;
      max-width: 900px;
      margin: 20px auto;
      padding: 20px;
    }
    h1, h2, h3 { color: #5c9eef; border-bottom: 2px solid #444; padding-bottom: 5px; }
    h1 { font-size: 2.5em; }
    h2 { font-size: 2em; margin-top: 1.5em; }
    h3 { font-size: 1.5em; margin-top: 1.2em; border-bottom: 1px solid #444; }
    h4 { font-size: 1.2em; color: #ccc; }
    img { max-width: 100%; height: auto; border-radius: 8px; margin-top: 10px; border: 1px solid #555; }
    .stat-block { 
      background-color: #2a2a2a; 
      border: 1px solid #555; 
      border-radius: 8px; 
      padding: 15px; 
      margin-top: 10px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
    .card { background-color: #252525; padding: 15px; border-radius: 8px; border: 1px solid #444; }
    .reward-item {
      background-color: #252525;
      padding: 10px 15px;
      border-radius: 8px;
      border: 1px solid #444;
      margin-bottom: 10px;
    }
    .reward-item strong { color: #87b9ff; }
    ul { padding-left: 20px; }
    p { margin-bottom: 1em; }
  `;

  return createHtmlTemplate(title, css, moduleData, images);
};

/**
 * Creates the self-contained HTML file content for printing (light theme).
 * @param {object} moduleData - The generated module JSON.
 * @param {object} images - The object of generated base64 image URLs.
 * @returns {string} - The full HTML document as a string.
 */
const createPrintHtml = (moduleData, images) => {
  const { title } = moduleData;

  const css = `
    body {
      font-family: "Georgia", "Times New Roman", Times, serif;
      line-height: 1.5;
      background-color: #ffffff;
      color: #000000;
      max-width: 100%;
      width: A4;
      margin: 0 auto;
      padding: 2cm;
      font-size: 12pt;
    }
    h1, h2, h3 { color: #333; border-bottom: 2px solid #ccc; padding-bottom: 5px; }
    h1 { font-size: 24pt; }
    h2 { font-size: 20pt; margin-top: 1.5em; page-break-before: auto; }
    h3 { font-size: 16pt; margin-top: 1.2em; border-bottom: 1px solid #ccc; }
    h4 { font-size: 14pt; color: #444; }
    img { 
      max-width: 100%; 
      height: auto; 
      border-radius: 4px; 
      margin-top: 10px; 
      border: 1px solid #ccc; 
      page-break-inside: avoid;
    }
    .stat-block { 
      background-color: #f9f9f9; 
      border: 1px solid #ccc; 
      border-radius: 5px; 
      padding: 15px; 
      margin-top: 10px;
      page-break-inside: avoid;
    }
    .grid { 
      display: grid; 
      grid-template-columns: 1fr; /* Single column for printing */
      gap: 15px; 
    }
    .card { 
      background-color: #fafafa; 
      padding: 15px; 
      border-radius: 5px; 
      border: 1px solid #ddd; 
      page-break-inside: avoid;
    }
    .reward-item {
      background-color: #fafafa;
      padding: 10px 15px;
      border-radius: 5px;
      border: 1px solid #ddd;
      margin-bottom: 10px;
      page-break-inside: avoid;
    }
    .reward-item strong { color: #005a9c; }
    ul { padding-left: 20px; }
    p { margin-bottom: 1em; }
    @media print {
      body {
        margin: 1cm;
        padding: 0;
      }
      h2 { page-break-before: always; }
      h1, h2, h3 { page-break-after: avoid; }
    }
  `;
  
  return createHtmlTemplate(title, css, moduleData, images);
};

/**
 * Generic HTML template builder.
 * @param {string} title - The document title.
 * @param {string} css - The CSS styles.
 * @param {object} moduleData - The generated module JSON.
 * @param {object} images - The object of generated base64 image URLs.
 * @returns {string} - The full HTML document as a string.
 */
const createHtmlTemplate = (title, css, moduleData, images) => {
  const {
    location, setup, plotHooks, mainPlotSteps,
    mainCharacters, monsterStatBlocks, rewardsList,
    generatedMagicItems, generatedPlotTwists // Get items from moduleData
  } = moduleData;

  const renderHtml = (html) => html || "<p>N/A</p>";
  
  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${title || "D&D Module"}</title>
      <style>${css}</style>
    </head>
    <body>
      <h1>${title || "Generated Module"}</h1>
      <h3>Location: ${location || "N/A"}</h3>
      
      <h2>Setup & Background</h2>
      ${renderHtml(setup)}
      
      <h2>Starting Point</h2>
      ${images.startPoint ? `<img src="${images.startPoint}" alt="Starting Point Scene" style="aspect-ratio: 16/9; object-fit: cover;">` : ""}
      
      <h2>Plot Hooks</h2>
      <div class="grid">
        ${(plotHooks || []).map(hook => `
          <div class="card">
            <h3>${hook.title}</h3>
            ${renderHtml(hook.description)}
          </div>
        `).join("")}
      </div>
      
      <h2>Main Plot Steps</h2>
      ${(mainPlotSteps || []).map((step, index) => `
        <div class="card" style="margin-bottom: 15px;">
          <h3>Step ${index + 1}: ${step.title}</h3>
          ${images.plotSteps?.[index] ? `<img src="${images.plotSteps[index]}" alt="Plot Step ${index + 1} Scene" style="aspect-ratio: 16/9; object-fit: cover; margin-bottom: 10px;">` : ""}
          ${renderHtml(step.description)}
        </div>
      `).join("")}

      <!-- NEW: Plot Twists Section -->
      ${(generatedPlotTwists || []).length > 0 ? `
        <h2>Plot Twists</h2>
        <div class="grid" style="margin-top: 20px;">
          ${(generatedPlotTwists || []).map(twist => `
            <div class="card">
              <h3>${twist.title}</h3>
              ${renderHtml(twist.description)}
            </div>
          `).join("")}
        </div>
      ` : ""}
      <!-- End of new section -->

      <h2>Regional Map</h2>
      ${images.regionMap ? `<img src="${images.regionMap}" alt="Regional Map" style="aspect-ratio: 16/9; object-fit: cover;">` : ""}

      <h2>Battle Map</h2>
      ${images.map ? `<img src="${images.map}" alt="Battle Map" style="aspect-ratio: 16/9; object-fit: cover;">` : ""}
      
      <h2>Main Characters</h2>
      <div class="grid">
        ${(mainCharacters || []).map((char, index) => `
          <div class="card">
            <h3>${char.name}</h3>
            ${images.characters?.[index] ? `<img src="${images.characters[index]}" alt="${char.name}" style="aspect-ratio: 1/1; object-fit: cover;">` : ""}
            ${renderHtml(char.description)}
            ${char.statBlock ? `<div class="stat-block"><h4>Stat Block</h4>${renderHtml(char.statBlock)}</div>` : ""}
          </div>
        `).join("")}
      </div>

      <h2>Monsters</h2>
      <div class="grid">
        ${(monsterStatBlocks || []).map((monster, index) => `
          <div class="card">
            <h3>${monster.name}</h3>
            ${images.monsters?.[index] ? `<img src="${images.monsters[index]}" alt="${monster.name}" style="aspect-ratio: 1/1; object-fit: cover;">` : ""}
            <div class="stat-block">
              ${renderHtml(monster.statBlock)}
            </div>
          </div>
        `).join("")}
      </div>

      <h2>Rewards</h2>
      ${images.rewards ? `<img src="${images.rewards}" alt="Module Rewards" style="aspect-ratio: 16/9; object-fit: cover;">` : ""}
      
      <div style="margin-top: 20px;">
        ${(rewardsList || []).map(reward => `
          <div class="reward-item">
            <h4>${reward.name} (<strong>${reward.value}</strong>)</h4>
            ${renderHtml(reward.description)}
          </div>
        `).join("")}
      </div>

      <!-- NEW: Added Magic Items -->
      ${(generatedMagicItems || []).length > 0 ? `
        <h3 style="margin-top: 1.5em; border-bottom: 1px solid #444;">Magic Items</h3>
        <div style="margin-top: 20px;">
          ${(generatedMagicItems || []).map(item => `
            <div class="reward-item">
              <h4>${item.name} (<strong>${item.value}</strong>)</h4>
              ${renderHtml(item.description)}
            </div>
          `).join("")}
        </div>
      ` : ""}
      <!-- End of new sections -->

    </body>
    </html>
  `;
};


// --- Main App Component ---

export default function App() {
  const [formData, setFormData] = useState({
    storyLinePrompt: "A village plagued by disappearances...", // NEW
    storyLine: "", // This will be populated by the AI
    otherThings: "Include a rival adventuring party and a moral dilemma.",
    rewards: "A magical moon-touched weapon and a hefty sum of gold.",
    level: 3,
    length: 4,
    creativity: 5,
    numPlayers: 4,
  });

  const [storyLineLoading, setStoryLineLoading] = useState(false); // NEW
  const [mainLoading, setMainLoading] = useState(false);
  const [mainError, setMainError] = useState(null);
  const [generatedModule, setGeneratedModule] = useState(null);
  
  // State for inspirational images
  const [inspirationalImages, setInspirationalImages] = useState([]); // { mimeType, data, originalUrl }
  
  // State for all images
  const [generatedImages, setGeneratedImages] = useState({
    rewards: null,
    startPoint: null,
    map: null,
    regionMap: null,
    characters: [],
    monsters: [],
    plotSteps: [], // For plot step images
  });
  
  // Separate loading state for each image
  const [imageLoadingStates, setImageLoadingStates] = useState({
    rewards: false,
    startPoint: false,
    map: false,
    regionMap: false,
    characters: [],
    monsters: [],
    plotSteps: [], // For plot step images
  });

  const handleFormChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value,
    }));
  };

  /**
   * Handles the interactive story line generation.
   */
  const handleGenerateStoryLine = async () => {
    if (!formData.storyLinePrompt) return;
    setStoryLineLoading(true);
    setMainError(null); // Clear main error on new action
    try {
      const prompt = `Expand the following D&D story idea into a compelling one-paragraph story line for a module. Keep it concise but atmospheric.
      
      Idea: "${formData.storyLinePrompt}"`;
      
      const expandedStory = await generateSimpleText(prompt);
      setFormData(prev => ({ ...prev, storyLine: expandedStory }));
    } catch (error) {
      console.warn("Failed to generate story line:", error); // Changed from console.error
      // Set main error to show the user what happened
      setMainError(`Story Line generation failed: ${error.message}`);
      // --- End of Fix ---
    } finally {
      setStoryLineLoading(false);
    }
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    files.forEach(file => {
      if (!file.type.startsWith('image/')) {
        console.warn(`File "${file.name}" is not an image and will be skipped.`);
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result;
        try {
          const [header, base64Data] = result.split(',');
          const mimeType = header.match(/:(.*?);/)[1];
          setInspirationalImages(prev => [
            ...prev,
            { mimeType, data: base64Data, originalUrl: result }
          ]);
        } catch (error) {
          console.error("Failed to read file:", error);
        }
      };
      reader.onerror = (error) => {
        console.error("FileReader error:", error);
      };
      reader.readAsDataURL(file);
    });
    
    // Reset file input value to allow re-uploading the same file
    e.target.value = null;
  };

  const handleRemoveImage = (indexToRemove) => {
    setInspirationalImages(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  const handleGenerateModule = async (e) => {
    e.preventDefault();
    
    if (!formData.storyLine) {
      setMainError("Please generate or write a story line before creating the module.");
      return;
    }

    setMainLoading(true);
    setMainError(null);
    setGeneratedModule(null);
    setGeneratedImages({ 
      rewards: null, 
      startPoint: null, 
      map: null, 
      regionMap: null, 
      characters: [], 
      monsters: [],
      plotSteps: [] // Reset plotSteps images
    });
    setImageLoadingStates({ 
      rewards: false, 
      startPoint: false, 
      map: false, 
      regionMap: false, 
      characters: [], 
      monsters: [],
      plotSteps: [] // Reset plotSteps loading
    });
    setInspirationalImages([]); // Clear inspirational images

    try {
      // 1. Generate Module Text (now includes items and twists)
      const moduleData = await generateModuleText(formData, inspirationalImages);
      setGeneratedModule(moduleData);
      setMainLoading(false); // Stop main loading *after* text gen

      // 2. Initialize Image Loading States
      setImageLoadingStates({
        rewards: true,
        startPoint: true,
        map: true,
        regionMap: true,
        characters: moduleData.mainCharacters.map(() => true),
        monsters: moduleData.monsterStatBlocks.map(() => true),
        plotSteps: moduleData.mainPlotSteps.map(() => true), // Initialize for plot steps
      });

      // 3. Kick off all image generation in parallel
      
      // Scene Images
      generateImage(moduleData.rewardsImagePrompt, '16:9')
        .then(url => {
          setGeneratedImages(prev => ({ ...prev, rewards: url }));
        })
        .catch(err => console.warn("Failed to generate rewards image:", err.message))
        .finally(() => {
          setImageLoadingStates(prev => ({ ...prev, rewards: false }));
        });

      generateImage(moduleData.startPointPrompt, '16:9')
        .then(url => {
          setGeneratedImages(prev => ({ ...prev, startPoint: url }));
        })
        .catch(err => console.warn("Failed to generate start point image:", err.message))
        .finally(() => {
          setImageLoadingStates(prev => ({ ...prev, startPoint: false }));
        });

      generateImage(moduleData.mapPrompt, '16:9')
        .then(url => {
          setGeneratedImages(prev => ({ ...prev, map: url }));
        })
        .catch(err => console.warn("Failed to generate map image:", err.message))
        .finally(() => {
          setImageLoadingStates(prev => ({ ...prev, map: false }));
        });

      generateImage(moduleData.regionMapPrompt, '16:9')
        .then(url => {
          setGeneratedImages(prev => ({ ...prev, regionMap: url }));
        })
        .catch(err => console.warn("Failed to generate region map image:", err.message))
        .finally(() => {
          setImageLoadingStates(prev => ({ ...prev, regionMap: false }));
        });

      // Character Images
      moduleData.mainCharacters.forEach((char, index) => {
        generateImage(char.imagePrompt, '1:1')
          .then(url => {
            setGeneratedImages(prev => {
              const newChars = [...prev.characters];
              newChars[index] = url;
              return { ...prev, characters: newChars };
            });
          })
          .catch(err => console.warn(`Failed to generate image for ${char.name}:`, err.message))
          .finally(() => {
            setImageLoadingStates(prev => {
              const newStates = [...prev.characters];
              newStates[index] = false;
              return { ...prev, characters: newStates };
            });
          });
      });
      
      // Monster Images
      moduleData.monsterStatBlocks.forEach((monster, index) => {
        generateImage(monster.imagePrompt, '1:1')
          .then(url => {
            setGeneratedImages(prev => {
              const newMonsters = [...prev.monsters];
              newMonsters[index] = url;
              return { ...prev, monsters: newMonsters };
            });
          })
          .catch(err => console.warn(`Failed to generate image for ${monster.name}:`, err.message))
          .finally(() => {
            setImageLoadingStates(prev => {
              const newStates = [...prev.monsters];
              newStates[index] = false;
              return { ...prev, monsters: newStates };
            });
          });
      });

      // Plot Step Images
      moduleData.mainPlotSteps.forEach((step, index) => {
        generateImage(step.imagePrompt, '16:9')
          .then(url => {
            setGeneratedImages(prev => {
              const newPlotSteps = [...prev.plotSteps];
              newPlotSteps[index] = url;
              return { ...prev, plotSteps: newPlotSteps };
            });
          })
          .catch(err => console.warn(`Failed to generate image for plot step ${index + 1}:`, err.message))
          .finally(() => {
            setImageLoadingStates(prev => {
              const newStates = [...prev.plotSteps];
              newStates[index] = false;
              return { ...prev, plotSteps: newStates };
            });
          });
      });

    } catch (error) {
      console.warn(error); // Changed from console.error
      setMainError(error.message);
      setMainLoading(false);
    }
  };

  const handleDownload = () => {
    if (!generatedModule) return;
    try {
      // Pass only module and images. Items/twists are *inside* module.
      const htmlContent = createDownloadHtml(generatedModule, generatedImages);
      const blob = new Blob([htmlContent], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${generatedModule.title.toLowerCase().replace(/\s+/g, '_') || 'dnd_module'}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to create download:", error);
      setMainError("Failed to prepare file for download.");
    }
  };
  
  const handlePrint = () => {
    if (!generatedModule) return;
    try {
      // Pass only module and images. Items/twists are *inside* module.
      const htmlContent = createPrintHtml(generatedModule, generatedImages);
      const printWindow = window.open('', '_blank');
      printWindow.document.write(htmlContent);
      printWindow.document.close();
      printWindow.focus();
      // Use setTimeout to ensure content is loaded before printing
      setTimeout(() => {
        printWindow.print();
        printWindow.close();
      }, 500);
    } catch (error) {
      console.error("Failed to create print version:", error);
      setMainError("Failed to prepare file for printing.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans">
      
      {/* --- Main Loading Overlay --- */}
      {mainLoading && (
        <div className="fixed inset-0 bg-black/80 z-50 flex flex-col items-center justify-center p-4 text-center">
          <style>
            {`
              @keyframes tumble {
                0% {
                  transform: perspective(800px) rotateX(0deg) rotateY(0deg) rotateZ(0deg);
                  opacity: 0.5;
                }
                25% {
                  transform: perspective(800px) rotateX(180deg) rotateY(90deg) rotateZ(45deg);
                  opacity: 1;
                }
                50% {
                  transform: perspective(800px) rotateX(360deg) rotateY(270deg) rotateZ(90deg);
                  opacity: 0.7;
                }
                75% {
                  transform: perspective(800px) rotateX(540deg) rotateY(360deg) rotateZ(135deg);
                  opacity: 1;
                }
                100% {
                  transform: perspective(800px) rotateX(720deg) rotateY(450deg) rotateZ(180deg);
                  opacity: 0.5;
                }
              }
              .dice-animation {
                transform-style: preserve-3d;
                animation: tumble 3s ease-in-out infinite;
                color: #DC2626; /* Red-600, inspired by the image */
              }
            `}
          </style>
          <Dices className="h-24 w-24 dice-animation mb-6" />
          <Loader2 className="animate-spin h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg text-gray-300 font-semibold">Rolling initiative for your campaign...</p>
          <p className="text-md text-gray-500 mt-2">Crafting worlds, characters, and epic quests!</p>
        </div>
      )}

      <div className="md:flex">
        {/* --- Left Input Panel --- */}
        <aside className="w-full md:w-1/3 lg:w-1/4 p-4 md:p-6 bg-gray-900 md:bg-gray-800/50 md:sticky top-0 h-screen overflow-y-auto border-r border-gray-700/50">
          <h1 className="text-2xl font-bold text-white mb-6">D&D Module Architect</h1>
          <form onSubmit={handleGenerateModule} className="space-y-4">
            
            {/* --- Interactive Story Line --- */}
            <div>
              <InputLabel htmlFor="storyLinePrompt">Story Line Prompt (This will generate the Story Line)</InputLabel>
              <div className="flex gap-2">
                <TextArea
                  id="storyLinePrompt"
                  name="storyLinePrompt"
                  rows="8" 
                  value={formData.storyLinePrompt}
                  onChange={handleFormChange}
                  placeholder="e.g., A traveling circus with a dark secret..."
                  className="flex-1"
                />
                <button
                  type="button"
                  onClick={handleGenerateStoryLine}
                  disabled={storyLineLoading}
                  className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
                  title="Generate Story Line"
                >
                  {storyLineLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Sparkles className="h-5 w-5" />}
                </button>
              </div>
            </div>
            <div>
              <InputLabel htmlFor="storyLine">Story Line</InputLabel>
              <TextArea
                id="storyLine"
                name="storyLine"
                rows="8" // Expanded to 8 lines
                value={formData.storyLine}
                onChange={handleFormChange}
                required
                placeholder="Click 'Generate' above or write your own..."
              />
            </div>
            {/* --- End of section --- */}
            
            <div>
              <InputLabel htmlFor="otherThings">Other Things to Include</InputLabel>
              <TextArea
                id="otherThings"
                name="otherThings"
                rows="4"
                value={formData.otherThings}
                onChange={handleFormChange}
              />
            </div>
            <div>
              <InputLabel htmlFor="rewards">Rewards to Include</InputLabel>
              <TextInput
                type="text"
                id="rewards"
                name="rewards"
                value={formData.rewards}
                onChange={handleFormChange}
                required
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <InputLabel htmlFor="numPlayers">Players</InputLabel>
                <TextInput
                  type="number"
                  id="numPlayers"
                  name="numPlayers"
                  min="1"
                  max="10"
                  value={formData.numPlayers}
                  onChange={handleFormChange}
                  required
                />
              </div>
              <div>
                <InputLabel htmlFor="level">Level</InputLabel>
                <TextInput
                  type="number"
                  id="level"
                  name="level"
                  min="1"
                  max="20"
                  value={formData.level}
                  onChange={handleFormChange}
                  required
                />
              </div>
              <div>
                <InputLabel htmlFor="length">Hours</InputLabel>
                <TextInput
                  type="number"
                  id="length"
                  name="length"
                  min="1"
                  max="20"
                  value={formData.length}
                  onChange={handleFormChange}
                  required
                />
              </div>
            </div>

            {/* --- Creativity Slider --- */}
            <div>
              <InputLabel htmlFor="creativity">
                Creativity Level: <span className="font-bold text-white">{formData.creativity}</span>
              </InputLabel>
              <input
                type="range"
                id="creativity"
                name="creativity"
                min="1"
                max="10"
                value={formData.creativity}
                onChange={handleFormChange}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer range-lg accent-blue-500"
              />
            </div>

            {/* --- Inspirational Images Upload --- */}
            <div className="space-y-2 pt-2">
              <InputLabel htmlFor="image-upload">Inspirational Images (Optional)</InputLabel>
              <label
                htmlFor="image-upload"
                className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-600 rounded-lg shadow-sm text-sm font-medium text-gray-300 bg-gray-700 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:ring-offset-gray-900 cursor-pointer"
              >
                <Paperclip className="h-5 w-5" />
                Upload Images
              </label>
              <input
                type="file"
                id="image-upload"
                multiple
                accept="image/*"
                onChange={handleImageUpload}
                className="sr-only"
              />
              {inspirationalImages.length > 0 && (
                <div className="grid grid-cols-3 gap-2 pt-2">
                  {inspirationalImages.map((image, index) => (
                    <div key={index} className="relative aspect-square rounded-md overflow-hidden border border-gray-700">
                      <img
                        src={image.originalUrl}
                        alt={`Inspiration ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                      <button
                        type="button"
                        onClick={() => handleRemoveImage(index)}
                        className="absolute top-1 right-1 bg-black/60 text-white rounded-full p-0.5 hover:bg-red-600"
                        aria-label="Remove image"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className="pt-4">
              <IconButton
                type="submit"
                icon={Wand2}
                text="Generate Module"
                loading={mainLoading}
                className="bg-blue-600 hover:bg-blue-700 focus:ring-blue-500"
              />
            </div>
          </form>
        </aside>

        {/* --- Right Output Panel --- */}
        <main className="w-full md:w-2/3 lg:w-3/4 p-4 md:p-8 lg:p-10 min-h-screen overflow-y-auto">
          {/* Main loading spinner is now an overlay */}

          {mainError && (
            <div className="max-w-2xl mx-auto">
              <ErrorDisplay message={mainError} />
            </div>
          )}

          {!mainLoading && !mainError && !generatedModule && (
            <div className="flex flex-col items-center justify-center h-[80vh] text-gray-500 text-center">
              <BookOpen className="h-24 w-24 mb-4" />
              <h2 className="text-2xl font-semibold">Your Adventure Awaits</h2>
              <p className="text-lg max-w-md">Fill out the form on the left and click "Generate Module" to begin creating your D&D adventure.</p>
            </div>
          )}
          
          {generatedModule && (
            <div className="max-w-4xl mx-auto">
              <div className="flex justify-between items-center mb-6 gap-4">
                <h1 className="text-4xl font-bold text-white flex-1">{generatedModule.title}</h1>
                <div className="flex gap-2">
                  <IconButton
                    icon={Printer}
                    text="Print"
                    onClick={handlePrint}
                    className="bg-gray-600 hover:bg-gray-700 focus:ring-gray-500 w-auto"
                    title="Open print-friendly version"
                  />
                  <IconButton
                    icon={Download}
                    text="Download"
                    onClick={handleDownload}
                    className="bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 w-auto"
                    title="Download dark-mode HTML"
                  />
                </div>
              </div>
              <p className="text-xl text-gray-400 mb-6 italic">Location: {generatedModule.location}</p>

              <Section title="Setup & Background" icon={BookOpen}>
                <HtmlRenderer htmlString={generatedModule.setup} />
              </Section>
              
              <Section title="Starting Point" icon={Eye}>
                <ImagePlaceholder
                  loading={imageLoadingStates.startPoint}
                  imageUrl={generatedImages.startPoint}
                  alt="Atmospheric starting point"
                  aspectRatio="16:9"
                />
              </Section>

              <Section title="Plot Hooks" icon={AlertTriangle}>
                <div className="grid md:grid-cols-2 gap-4">
                  {generatedModule.plotHooks.map((hook, index) => (
                    <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                      <h3 className="text-lg font-semibold text-white mb-2">{hook.title}</h3>
                      <HtmlRenderer htmlString={hook.description} />
                    </div>
                  ))}
                </div>
              </Section>
              
              <Section title="Main Plot" icon={BookOpen}>
                <div className="space-y-4">
                  {generatedModule.mainPlotSteps.map((step, index) => (
                    <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                      <h3 className="text-lg font-semibold text-white mb-2">Step {index + 1}: {step.title}</h3>
                      <ImagePlaceholder
                        loading={imageLoadingStates.plotSteps[index]}
                        imageUrl={generatedImages.plotSteps[index]}
                        alt={`Plot Step ${index + 1} Scene`}
                        aspectRatio="16:9"
                      />
                      <div className="mt-4">
                        <HtmlRenderer htmlString={step.description} />
                      </div>
                    </div>
                  ))}
                </div>
              </Section>

              {/* --- Plot Twists Section --- */}
              {generatedModule.generatedPlotTwists && generatedModule.generatedPlotTwists.length > 0 && (
                <Section title="Plot Twists" icon={Shuffle}>
                  <div className="grid md:grid-cols-2 gap-4">
                    {generatedModule.generatedPlotTwists.map((twist, index) => (
                      <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                        <h3 className="text-lg font-semibold text-white mb-2">{twist.title}</h3>
                        <HtmlRenderer htmlString={twist.description} />
                      </div>
                    ))}
                  </div>
                </Section>
              )}
              {/* --- End of section --- */}

              <Section title="Regional Map" icon={Map}>
                <ImagePlaceholder
                  loading={imageLoadingStates.regionMap}
                  imageUrl={generatedImages.regionMap}
                  alt="Regional Map"
                  aspectRatio="16:9"
                />
              </Section>

              <Section title="Battle Map" icon={Map}>
                <ImagePlaceholder
                  loading={imageLoadingStates.map}
                  imageUrl={generatedImages.map}
                  alt="Top-down battle map"
                  aspectRatio="16:9"
                />
              </Section>
              
              <Section title="Main Characters" icon={BookOpen}>
                <div className="grid md:grid-cols-2 gap-6">
                  {generatedModule.mainCharacters.map((char, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                      <ImagePlaceholder
                        loading={imageLoadingStates.characters[index]}
                        imageUrl={generatedImages.characters[index]}
                        alt={char.name}
                        aspectRatio="1:1"
                      />
                      <div className="p-4">
                        <h3 className="text-xl font-bold text-white">{char.name}</h3>
                        <HtmlRenderer htmlString={char.description} />
                        {char.statBlock && (
                          <div className="mt-4 p-3 bg-gray-900/50 rounded-md border border-gray-700">
                            <h4 className="font-semibold text-gray-300 mb-2">Stat Block</h4>
                            <HtmlRenderer htmlString={char.statBlock} />
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </Section>
              
              <Section title="Monsters" icon={BookOpen}>
                <div className="grid md:grid-cols-2 gap-6">
                  {generatedModule.monsterStatBlocks.map((monster, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                      <ImagePlaceholder
                        loading={imageLoadingStates.monsters[index]}
                        imageUrl={generatedImages.monsters[index]}
                        alt={monster.name}
                        aspectRatio="1:1"
                      />
                      <div className="p-4">
                        <h3 className="text-xl font-bold text-white">{monster.name}</h3>
                         <div className="mt-2 p-3 bg-gray-900/50 rounded-md border border-gray-700">
                           <HtmlRenderer htmlString={monster.statBlock} />
                         </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Section>

              <Section title="Rewards" icon={Gift}>
                <ImagePlaceholder
                  loading={imageLoadingStates.rewards}
                  imageUrl={generatedImages.rewards}
                  alt="Module rewards"
                  aspectRatio="16:9"
                />
                <div className="space-y-3 mt-4">
                  {generatedModule.rewardsList.map((reward, index) => (
                    <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                      <h4 className="text-lg font-semibold text-white">
                        {reward.name} (<span className="text-blue-300 font-medium">{reward.value}</span>)
                      </h4>
                      <HtmlRenderer htmlString={reward.description} />
                    </div>
                  ))}
                </div>

                {/* --- Display for Magic Items --- */}
                {generatedModule.generatedMagicItems && generatedModule.generatedMagicItems.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-xl font-semibold text-white mb-3 pt-3 border-t border-gray-700">Magic Items</h3>
                    <div className="space-y-3">
                      {generatedModule.generatedMagicItems.map((item, index) => (
                        <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                          <h4 className="text-lg font-semibold text-white">
                            {item.name} (<span className="text-blue-300 font-medium">{item.value}</span>)
                          </h4>
                          <HtmlRenderer htmlString={item.description} />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {/* --- End of display --- */}
              </Section>
              
              {/* --- Second Download/Print Button --- */}
              <div className="mt-8 pt-6 border-t border-gray-700 flex gap-4">
                <IconButton
                  icon={Printer}
                  text="Print"
                  onClick={handlePrint}
                  disabled={mainLoading} // Disable if still generating
                  className="bg-gray-600 hover:bg-gray-700 focus:ring-gray-500"
                  title="Open print-friendly version"
                />
                <IconButton
                  icon={Download}
                  text="Download"
                  onClick={handleDownload}
                  disabled={mainLoading} // Disable if still generating
                  className="bg-blue-600 hover:bg-blue-700 focus:ring-blue-500"
                  title="Download dark-mode HTML"
                />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}