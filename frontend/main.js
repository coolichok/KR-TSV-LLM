// Глобальные переменные
let editor = null;
let currentPage = 1;
let perPage = 12;
let currentFilters = {};
let currentExplanationId = null;

// Базовый URL API
const API_BASE_URL = 'http://localhost:8000';

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // Определяем, главный экран открыт или страница истории
        const isHistoryPage = window.location.pathname.includes('history.html');
        
        if (!isHistoryPage) {
            // Инициализируем главную страницу
            await initializeMainPage();
        } else {
            // Инициализируем страницу истории
            await initializeHistoryPage();
        }
    } catch (error) {
        console.error('Error initializing app:', error);
        showNotification('Failed to initialize application', 'error');
    }
}

// Main Page Functions
async function initializeMainPage() {
    try {
        // Инициализируем редактор Monaco
        await initializeMonacoEditor();
        
        // Загружаем список языков
        await loadLanguages();
        
        // Настраиваем обработчики событий
        setupMainPageEventListeners();
        
        // Загружаем пример кода
        loadExampleCode();
        
    } catch (error) {
        console.error('Error initializing main page:', error);
    }
}

async function initializeMonacoEditor() {
    return new Promise((resolve) => {
        require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' } });
        require(['vs/editor/editor.main'], function () {
            editor = monaco.editor.create(document.getElementById('codeEditor'), {
                value: '',
                language: 'python',
                theme: 'vs-light',
                automaticLayout: true,
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                wordWrap: 'on'
            });
            resolve();
        });
    });
}

async function loadLanguages() {
    try {
        const response = await fetch(`${API_BASE_URL}/code/languages`);
        const data = await response.json();
        
        const languageSelect = document.getElementById('languageSelect');
        languageSelect.innerHTML = '<option value="auto">Auto-detect</option>';
        
        data.languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.value;
            option.textContent = `${lang.icon} ${lang.name}`;
            languageSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading languages:', error);
    }
}

function setupMainPageEventListeners() {
    // Кнопка «Explain Code»
    document.getElementById('explainButton').addEventListener('click', explainCode);
    
    // Кнопка очистки кода
    document.getElementById('clearCode').addEventListener('click', clearCode);
    
    // Кнопка загрузки примера
    document.getElementById('loadExample').addEventListener('click', loadExampleCode);
    
    // Кнопка копирования объяснения
    document.getElementById('copyExplanation').addEventListener('click', copyExplanation);
    
    // Кнопка сохранения объяснения
    document.getElementById('saveExplanation').addEventListener('click', saveExplanation);
}

async function explainCode() {
    const code = editor.getValue();
    const language = document.getElementById('languageSelect').value;
    const complexity = document.getElementById('complexitySelect').value;
    
    if (!code.trim()) {
        showNotification('Please enter some code to explain', 'warning');
        return;
    }
    
    // Отображаем состояние загрузки
    showLoadingState();
    
    try {
        const response = await fetch(`${API_BASE_URL}/code/explain`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code_snippet: code,
                language: language === 'auto' ? null : language,
                complexity_level: complexity
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayExplanation(data);
            showNotification('Explanation generated successfully!', 'success');
        } else {
            throw new Error(data.detail || 'Failed to generate explanation');
        }
        
    } catch (error) {
        console.error('Error explaining code:', error);
        showNotification('Failed to generate explanation. Please try again.', 'error');
        hideLoadingState();
    }
}

function showLoadingState() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('explanationContent').classList.add('hidden');
    document.getElementById('explainButton').disabled = true;
    document.getElementById('explainButton').innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Analyzing...';
}

function hideLoadingState() {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('explanationContent').classList.remove('hidden');
    document.getElementById('explainButton').disabled = false;
    document.getElementById('explainButton').innerHTML = '<i class="fas fa-magic mr-2"></i>Explain Code';
}

function displayExplanation(data) {
    hideLoadingState();
    
    const content = document.getElementById('explanationContent');
    content.innerHTML = `
        <div class="fade-in">
            ${data.explanation}
        </div>
    `;
    
    // Активируем кнопки действий
    document.getElementById('copyExplanation').disabled = false;
    document.getElementById('saveExplanation').disabled = false;
    
    // Обновляем статистику
    document.getElementById('processingTime').textContent = `${data.processing_time || '-'}s`;
    document.getElementById('languageDetected').textContent = data.language || '-';
    document.getElementById('codeComplexity').textContent = data.complexity_level || '-';
    document.getElementById('explanationStats').classList.remove('hidden');
}

function clearCode() {
    if (editor) {
        editor.setValue('');
    }
    document.getElementById('explanationContent').innerHTML = `
        <div class="text-center py-12 text-gray-500">
            <i class="fas fa-robot text-6xl mb-4"></i>
            <p class="text-lg">Submit your code to get an AI-powered explanation</p>
            <p class="text-sm mt-2">The explanation will appear here with detailed analysis</p>
        </div>
    `;
    document.getElementById('explanationStats').classList.add('hidden');
    document.getElementById('copyExplanation').disabled = true;
    document.getElementById('saveExplanation').disabled = true;
}

function loadExampleCode() {
    const examples = {
        python: `# Пример на Python: последовательность Фибоначчи
def fibonacci(n):
    """Формирует последовательность Фибоначчи из n элементов"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    sequence = [0, 1]
    for i in range(2, n):
        next_num = sequence[i-1] + sequence[i-2]
        sequence.append(next_num)
    
    return sequence

# Пример использования
result = fibonacci(10)
print(f"Первые 10 чисел Фибоначчи: {result}")`,
        
        javascript: `// Пример на JavaScript: сортировка массива с компаратором
function customSort(arr, compareFn) {
    // Создаём копию, чтобы не менять исходный массив
    const sorted = [...arr];
    
    // Для наглядности используем пузырьковую сортировку
    for (let i = 0; i < sorted.length - 1; i++) {
        for (let j = 0; j < sorted.length - i - 1; j++) {
            if (compareFn(sorted[j], sorted[j + 1]) > 0) {
                // Меняем элементы местами
                [sorted[j], sorted[j + 1]] = [sorted[j + 1], sorted[j]];
            }
        }
    }
    
    return sorted;
}

// Пример использования
const numbers = [64, 34, 25, 12, 22, 11, 90];
const sorted = customSort(numbers, (a, b) => a - b);
console.log('Отсортированный массив:', sorted);`,
        
        java: `// Пример на Java: реализация бинарного поиска
public class BinarySearch {
    
    public static int binarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (arr[mid] == target) {
                return mid; // Элемент найден
            } else if (arr[mid] < target) {
                left = mid + 1; // Ищем правее
            } else {
                right = mid - 1; // Ищем левее
            }
        }
        
        return -1; // Элемент не найден
    }
    
    public static void main(String[] args) {
        int[] sortedArray = {1, 3, 5, 7, 9, 11, 13, 15};
        int target = 7;
        int result = binarySearch(sortedArray, target);
        
        if (result != -1) {
            System.out.println("Элемент найден по индексу: " + result);
        } else {
            System.out.println("Элемент не найден");
        }
    }
}`
    };
    
    // Randomly select an example
    const languages = Object.keys(examples);
    const randomLang = languages[Math.floor(Math.random() * languages.length)];
    
    if (editor) {
        editor.setValue(examples[randomLang]);
        editor.setLanguage(randomLang);
        document.getElementById('languageSelect').value = randomLang;
    }
    
    showNotification(`Loaded ${randomLang} example code`, 'info');
}

async function copyExplanation() {
    const explanationContent = document.getElementById('explanationContent').textContent;
    
    try {
        await navigator.clipboard.writeText(explanationContent);
        showNotification('Explanation copied to clipboard!', 'success');
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        showNotification('Failed to copy explanation', 'error');
    }
}

async function saveExplanation() {
    // Здесь можно было бы реализовать сохранение в настройки пользователя или localStorage
    showNotification('Explanation saved to favorites!', 'success');
}

// Функции страницы истории
async function initializeHistoryPage() {
    try {
        setupHistoryPageEventListeners();
        await loadHistory();
        await loadLanguageFilter();
    } catch (error) {
        console.error('Error initializing history page:', error);
    }
}

function setupHistoryPageEventListeners() {
    // Обработчики для фильтров
    document.getElementById('languageFilter').addEventListener('change', applyFilters);
    document.getElementById('complexityFilter').addEventListener('change', applyFilters);
    document.getElementById('favoriteFilter').addEventListener('change', applyFilters);
    document.getElementById('searchInput').addEventListener('input', debounce(applyFilters, 300));
    
    // Кнопки действий
    document.getElementById('clearFilters').addEventListener('click', clearFilters);
    document.getElementById('refreshHistory').addEventListener('click', loadHistory);
    
    // Пагинация
    document.getElementById('prevPage').addEventListener('click', () => changePage(-1));
    document.getElementById('nextPage').addEventListener('click', () => changePage(1));
    
    // Обработчики модального окна
    document.getElementById('closeModal').addEventListener('click', closeModal);
    document.getElementById('modalFavorite').addEventListener('click', toggleModalFavorite);
    document.getElementById('modalDelete').addEventListener('click', deleteModalExplanation);
    document.getElementById('modalCopy').addEventListener('click', copyModalExplanation);
    
    // Закрытие модального окна при клике вне его
    document.getElementById('explanationModal').addEventListener('click', (e) => {
        if (e.target.id === 'explanationModal') {
            closeModal();
        }
    });
}

async function loadLanguageFilter() {
    try {
        const response = await fetch(`${API_BASE_URL}/code/languages`);
        const data = await response.json();
        
        const languageFilter = document.getElementById('languageFilter');
        languageFilter.innerHTML = '<option value="">All Languages</option>';
        
        data.languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.value;
            option.textContent = `${lang.icon} ${lang.name}`;
            languageFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading language filter:', error);
    }
}

async function loadHistory() {
    showHistoryLoading();
    
    try {
        const params = new URLSearchParams({
            page: currentPage,
            per_page: perPage,
            ...currentFilters
        });
        
        const response = await fetch(`${API_BASE_URL}/history/explanations?${params}`);
        const data = await response.json();
        
        if (data.success) {
            displayHistory(data);
            updateHistoryStats(data);
        } else {
            throw new Error('Failed to load history');
        }
        
    } catch (error) {
        console.error('Error loading history:', error);
        showHistoryError();
    }
}

function showHistoryLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('historyItems').classList.add('hidden');
}

function displayHistory(data) {
    document.getElementById('loadingState').classList.add('hidden');
    
        if (data.explanations.length === 0) {
        document.getElementById('emptyState').classList.remove('hidden');
        document.getElementById('historyItems').classList.add('hidden');
        return;
    }
    
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('historyItems').classList.remove('hidden');
    
    const container = document.getElementById('historyItems');
    container.innerHTML = '';
    
    data.explanations.forEach(item => {
        const historyCard = createHistoryCard(item);
        container.appendChild(historyCard);
    });
    
    // Обновляем состояние пагинации
    updatePagination(data);
}

function createHistoryCard(item) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-lg p-6 hover-lift fade-in cursor-pointer';
    card.onclick = () => openModal(item);
    
    const languageIcon = getLanguageIcon(item.language);
    const complexityIcon = getComplexityIcon(item.complexity_level);
    
    card.innerHTML = `
        <div class="flex justify-between items-start mb-4">
            <div class="flex items-center space-x-2">
                <span class="text-2xl">${languageIcon}</span>
                <div>
                    <div class="font-semibold text-gray-900 capitalize">${item.language}</div>
                    <div class="text-sm text-gray-600">${complexityIcon} ${item.complexity_level}</div>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                ${item.is_favorite ? '<i class="fas fa-heart text-red-500"></i>' : ''}
                <button onclick="event.stopPropagation(); toggleFavorite(${item.id}, ${!item.is_favorite})" 
                        class="text-gray-400 hover:text-red-500 p-1">
                    <i class="fas fa-heart${item.is_favorite ? '' : '-o'}"></i>
                </button>
            </div>
        </div>
        
        <div class="mb-4">
            <div class="code-preview mb-3">${escapeHtml(item.code_snippet.substring(0, 200))}${item.code_snippet.length > 200 ? '...' : ''}</div>
        </div>
        
        <div class="explanation-preview text-sm text-gray-600 mb-4">
            ${stripHtml(item.explanation.substring(0, 300))}${item.explanation.length > 300 ? '...' : ''}
        </div>
        
        <div class="flex justify-between items-center text-sm text-gray-500">
            <span>${formatDate(item.created_at)}</span>
            <div class="space-x-2">
                <button onclick="event.stopPropagation(); openModal(${JSON.stringify(item).replace(/"/g, '&quot;')})" 
                        class="text-indigo-600 hover:text-indigo-800">
                    <i class="fas fa-eye mr-1"></i>View
                </button>
                <button onclick="event.stopPropagation(); deleteExplanation(${item.id})" 
                        class="text-red-600 hover:text-red-800">
                    <i class="fas fa-trash mr-1"></i>Delete
                </button>
            </div>
        </div>
    `;
    
    return card;
}

function getLanguageIcon(language) {
    const icons = {
        python: '🐍',
        javascript: '🟨',
        java: '☕',
        cpp: '⚡',
        csharp: '🔷',
        php: '🐘',
        ruby: '💎',
        go: '🐹',
        rust: '🦀',
        typescript: '🔷',
        html: '🌐',
        css: '🎨',
        sql: '🗄️',
        bash: '🐚'
    };
    return icons[language] || '💻';
}

function getComplexityIcon(complexity) {
    const icons = {
        beginner: '🌱',
        intermediate: '🎯',
        advanced: '🚀'
    };
    return icons[complexity] || '📝';
}

function updateHistoryStats(data) {
    document.getElementById('totalCount').textContent = data.total_count || 0;
    document.getElementById('currentRange').textContent = `${(currentPage - 1) * perPage + 1}-${Math.min(currentPage * perPage, data.total_count)}`;
    document.getElementById('totalFiltered').textContent = data.total_count || 0;
}

function updatePagination(data) {
    const pagination = document.getElementById('pagination');
    
    if (data.total_pages > 1) {
        pagination.classList.remove('hidden');
        
        document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${data.total_pages}`;
        document.getElementById('prevPage').disabled = currentPage === 1;
        document.getElementById('nextPage').disabled = currentPage === data.total_pages;
    } else {
        pagination.classList.add('hidden');
    }
}

async function applyFilters() {
    currentFilters = {};
    
    const language = document.getElementById('languageFilter').value;
    const complexity = document.getElementById('complexityFilter').value;
    const favorite = document.getElementById('favoriteFilter').value;
    const search = document.getElementById('searchInput').value;
    
    if (language) currentFilters.language = language;
    if (complexity) currentFilters.complexity_level = complexity;
    if (favorite !== '') currentFilters.is_favorite = favorite;
    if (search) currentFilters.search_term = search;
    
    currentPage = 1;
    await loadHistory();
}

function clearFilters() {
    document.getElementById('languageFilter').value = '';
    document.getElementById('complexityFilter').value = '';
    document.getElementById('favoriteFilter').value = '';
    document.getElementById('searchInput').value = '';
    
    currentFilters = {};
    currentPage = 1;
    loadHistory();
}

async function changePage(direction) {
    currentPage += direction;
    await loadHistory();
}

async function toggleFavorite(id, isFavorite) {
    try {
        const response = await fetch(`${API_BASE_URL}/history/explanations/${id}/favorite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                explanation_id: id,
                is_favorite: isFavorite
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            loadHistory();
        } else {
            throw new Error('Failed to update favorite status');
        }
        
    } catch (error) {
        console.error('Error updating favorite:', error);
        showNotification('Failed to update favorite status', 'error');
    }
}

async function deleteExplanation(id) {
    if (!confirm('Are you sure you want to delete this explanation?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/history/explanations/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Explanation deleted successfully', 'success');
            loadHistory();
        } else {
            throw new Error('Failed to delete explanation');
        }
        
    } catch (error) {
        console.error('Error deleting explanation:', error);
        showNotification('Failed to delete explanation', 'error');
    }
}

// Функции модального окна
function openModal(item) {
    currentExplanationId = item.id;
    
    document.getElementById('modalCode').textContent = item.code_snippet;
    document.getElementById('modalLanguage').textContent = `Language: ${item.language}`;
    document.getElementById('modalComplexity').textContent = `Complexity: ${item.complexity_level}`;
    document.getElementById('modalDate').textContent = `Date: ${formatDate(item.created_at)}`;
    document.getElementById('modalExplanation').innerHTML = item.explanation;
    
    // Update favorite button
    const favoriteBtn = document.getElementById('modalFavorite');
    if (item.is_favorite) {
        favoriteBtn.innerHTML = '<i class="fas fa-heart mr-2"></i>Remove from Favorites';
        favoriteBtn.classList.add('text-red-600');
    } else {
        favoriteBtn.innerHTML = '<i class="fas fa-heart mr-2"></i>Add to Favorites';
        favoriteBtn.classList.remove('text-red-600');
    }
    
    document.getElementById('explanationModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('explanationModal').classList.add('hidden');
    document.body.style.overflow = 'auto';
    currentExplanationId = null;
}

async function toggleModalFavorite() {
    if (!currentExplanationId) return;
    
    const favoriteBtn = document.getElementById('modalFavorite');
    const isCurrentlyFavorite = favoriteBtn.classList.contains('text-red-600');
    
    await toggleFavorite(currentExplanationId, !isCurrentlyFavorite);
    
    // Update modal button
    if (!isCurrentlyFavorite) {
        favoriteBtn.innerHTML = '<i class="fas fa-heart mr-2"></i>Remove from Favorites';
        favoriteBtn.classList.add('text-red-600');
    } else {
        favoriteBtn.innerHTML = '<i class="fas fa-heart mr-2"></i>Add to Favorites';
        favoriteBtn.classList.remove('text-red-600');
    }
    
    loadHistory();
}

async function deleteModalExplanation() {
    if (!currentExplanationId || !confirm('Are you sure you want to delete this explanation?')) {
        return;
    }
    
    await deleteExplanation(currentExplanationId);
    closeModal();
}

async function copyModalExplanation() {
    const explanation = document.getElementById('modalExplanation').textContent;
    
    try {
        await navigator.clipboard.writeText(explanation);
        showNotification('Explanation copied to clipboard!', 'success');
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        showNotification('Failed to copy explanation', 'error');
    }
}

// Вспомогательные функции
function showHistoryError() {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('emptyState').classList.remove('hidden');
    document.getElementById('historyItems').classList.add('hidden');
    document.getElementById('emptyState').innerHTML = `
        <div class="text-6xl text-red-300 mb-4">
            <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3 class="text-xl font-semibold text-red-600 mb-2">Error Loading History</h3>
        <p class="text-gray-500 mb-4">Failed to load your code history. Please try again.</p>
        <button onclick="loadHistory()" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg">
            <i class="fas fa-sync-alt mr-2"></i>Try Again
        </button>
    `;
}

function showNotification(message, type = 'info') {
    // Создаём элемент уведомления
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transform transition-all duration-300 translate-x-full`;
    
    // Определяем стиль уведомления в зависимости от типа
    const styles = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-black',
        info: 'bg-blue-500 text-white'
    };
    
    notification.className += ` ${styles[type] || styles.info}`;
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${getNotificationIcon(type)} mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Удаление через 3 секунды
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function stripHtml(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}