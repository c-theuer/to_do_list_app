import streamlit as st
from datetime import datetime

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'categories' not in st.session_state:
    st.session_state.categories = []
if 'next_task_id' not in st.session_state:
    st.session_state.next_task_id = 1
if 'next_category_id' not in st.session_state:
    st.session_state.next_category_id = 1
if 'editing_task_id' not in st.session_state:
    st.session_state.editing_task_id = None
if 'show_add_task' not in st.session_state:
    st.session_state.show_add_task = False
if 'show_add_category' not in st.session_state:
    st.session_state.show_add_category = False
if 'selected_cat_to_edit' not in st.session_state:
    st.session_state.selected_cat_to_edit = None


# Helper functions
def get_category_by_id(category_id):
    """Get category object by ID"""
    for cat in st.session_state.categories:
        if cat['id'] == category_id:
            return cat
    return None


def get_category_by_name(name):
    """Get category object by name"""
    for cat in st.session_state.categories:
        if cat['description'].lower() == name.lower():
            return cat
    return None


def get_task_by_id(task_id):
    """Get task object by ID"""
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            return task
    return None


def add_category(description, color):
    """Add a new category"""
    # Check if category with this name already exists
    if get_category_by_name(description):
        return None

    category = {
        'id': st.session_state.next_category_id,
        'description': description,
        'color': color
    }
    st.session_state.categories.append(category)
    st.session_state.next_category_id += 1
    return category['id']


def edit_category(category_id, description, color):
    """Edit an existing category"""
    # Check if another category with this name already exists
    existing = get_category_by_name(description)
    if existing and existing['id'] != category_id:
        return False

    category = get_category_by_id(category_id)
    if category:
        category['description'] = description
        category['color'] = color
        return True
    return False


def add_task(description, deadline=None, category_ids=None):
    """Add a new task"""
    task = {
        'id': st.session_state.next_task_id,
        'description': description,
        'categories': category_ids if category_ids else [],
        'deadline': deadline,
        'complete': False
    }
    st.session_state.tasks.append(task)
    st.session_state.next_task_id += 1
    return task['id']


def edit_task(task_id, description, deadline, category_ids):
    """Edit an existing task"""
    task = get_task_by_id(task_id)
    if task:
        task['description'] = description
        task['deadline'] = deadline
        task['categories'] = category_ids
        return True
    return False


def mark_task_complete(task_id, complete):
    """Mark task as complete or incomplete"""
    task = get_task_by_id(task_id)
    if task:
        task['complete'] = complete
        return True
    return False


def delete_task(task_id):
    """Delete a task"""
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]


def delete_category(category_id):
    """Delete a category"""
    st.session_state.categories = [c for c in st.session_state.categories if c['id'] != category_id]
    # Remove category from all tasks
    for task in st.session_state.tasks:
        if category_id in task['categories']:
            task['categories'].remove(category_id)


def get_filtered_tasks(category_filter=None, show_completed=True):
    """Get tasks filtered by category and completion status"""
    filtered = st.session_state.tasks

    if category_filter:
        filtered = [t for t in filtered if category_filter in t['categories']]

    if not show_completed:
        filtered = [t for t in filtered if not t['complete']]

    return filtered


# App UI
st.title("📝 To-Do List App")

# Sidebar for categories management
st.sidebar.header("📁 Categories")

# Add New Category Section
if st.session_state.show_add_category:
    with st.sidebar.container():
        st.markdown("**➕ Add New Category**")
        new_cat_desc = st.text_input("Category Name", key="new_cat_desc")
        new_cat_color = st.color_picker("Category Color", "#1f77b4", key="new_cat_color")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add", key="add_cat_btn"):
                if new_cat_desc.strip():
                    result = add_category(new_cat_desc, new_cat_color)
                    if result:
                        st.session_state.show_add_category = False
                        st.success(f"Category '{new_cat_desc}' added!")
                        st.rerun()
                    else:
                        st.session_state.cat_add_error = f"Category '{new_cat_desc}' already exists!"
                else:
                    st.session_state.cat_add_error = "Please enter a category name."
        with col2:
            if st.button("Cancel", key="cancel_add_cat"):
                st.session_state.show_add_category = False
                if 'cat_add_error' in st.session_state:
                    del st.session_state.cat_add_error
                st.rerun()

        # Display error/warning outside of columns
        if 'cat_add_error' in st.session_state:
            if "already exists" in st.session_state.cat_add_error:
                st.error(st.session_state.cat_add_error)
            else:
                st.warning(st.session_state.cat_add_error)
            del st.session_state.cat_add_error

        st.divider()
else:
    if st.sidebar.button("➕ Add New Category", key="show_add_cat_btn"):
        st.session_state.show_add_category = True
        st.rerun()

with st.sidebar.expander("✏️ Edit Categories", expanded=False):
    if st.session_state.categories:
        cat_to_edit = st.selectbox(
            "Select Category to Edit",
            options=[c['id'] for c in st.session_state.categories],
            format_func=lambda x: get_category_by_id(x)['description'],
            key="cat_to_edit"
        )

        # Update selected category if it changed
        if cat_to_edit != st.session_state.selected_cat_to_edit:
            st.session_state.selected_cat_to_edit = cat_to_edit

        if cat_to_edit:
            current_cat = get_category_by_id(cat_to_edit)

            # Use unique keys that include the category ID to force re-rendering
            edit_cat_desc = st.text_input(
                "Category Name",
                value=current_cat['description'],
                key=f"edit_cat_desc_{cat_to_edit}"
            )
            edit_cat_color = st.color_picker(
                "Category Color",
                current_cat['color'],
                key=f"edit_cat_color_{cat_to_edit}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_cat_btn_{cat_to_edit}"):
                    if edit_cat_desc.strip():
                        result = edit_category(cat_to_edit, edit_cat_desc, edit_cat_color)
                        if result:
                            st.success("Category updated!")
                            st.rerun()
                        else:
                            st.session_state.cat_edit_error = f"Category '{edit_cat_desc}' already exists!"
                    else:
                        st.session_state.cat_edit_error = "Category name cannot be empty."

            with col2:
                if st.button("Delete", key=f"delete_cat_btn_{cat_to_edit}", type="secondary"):
                    delete_category(cat_to_edit)
                    st.session_state.selected_cat_to_edit = None
                    st.success("Category deleted!")
                    st.rerun()

            # Display error/warning outside of columns
            if 'cat_edit_error' in st.session_state:
                if "already exists" in st.session_state.cat_edit_error:
                    st.error(st.session_state.cat_edit_error)
                else:
                    st.warning(st.session_state.cat_edit_error)
                del st.session_state.cat_edit_error
    else:
        st.info("No categories yet.")

# Display current categories
if st.session_state.categories:
    st.sidebar.subheader("Current Categories")
    for cat in st.session_state.categories:
        st.sidebar.markdown(
            f"<span style='color: {cat['color']}'>●</span> {cat['description']}",
            unsafe_allow_html=True
        )

# Main content
st.header("Your Tasks")

# Add Task Section (collapsible)
if st.session_state.show_add_task:
    with st.container():
        st.markdown("### ➕ Add New Task")

        new_task_desc = st.text_area("Task Description *", key="new_task_desc")

        col1, col2 = st.columns(2)
        with col1:
            new_task_deadline = st.date_input(
                "Deadline (Optional)",
                value=None,
                key="new_task_deadline"
            )

        with col2:
            if st.session_state.categories:
                new_task_categories = st.multiselect(
                    "Categories (Optional)",
                    options=[c['id'] for c in st.session_state.categories],
                    format_func=lambda x: get_category_by_id(x)['description'],
                    key="new_task_categories"
                )
            else:
                new_task_categories = []
                st.info("No categories available.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Add Task", key="add_task_btn", type="primary"):
                if new_task_desc.strip():
                    add_task(new_task_desc, new_task_deadline, new_task_categories)
                    st.session_state.show_add_task = False
                    st.success("Task added successfully!")
                    st.rerun()
                else:
                    st.warning("Please enter a task description.")

        with col2:
            if st.button("❌ Cancel", key="cancel_add_task"):
                st.session_state.show_add_task = False
                st.rerun()

        st.divider()
else:
    if st.button("➕ Add New Task", key="show_add_task_btn", type="primary"):
        st.session_state.show_add_task = True
        st.rerun()
    st.divider()

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    category_options = [None] + [c['id'] for c in st.session_state.categories]
    category_labels = ["All Categories"] + [c['description'] for c in st.session_state.categories]

    selected_filter_idx = st.selectbox(
        "Filter by Category",
        range(len(category_options)),
        format_func=lambda x: category_labels[x],
        key="category_filter"
    )
    category_filter = category_options[selected_filter_idx]

with col2:
    sort_option = st.selectbox(
        "Sort by",
        ["None", "Deadline (Earliest First)", "Deadline (Latest First)"],
        key="sort_option"
    )

with col3:
    show_completed = st.checkbox("Show Completed Tasks", value=True, key="show_completed")

# Get filtered tasks
filtered_tasks = get_filtered_tasks(category_filter, show_completed)

# Sort tasks based on selection
if sort_option == "Deadline (Earliest First)":
    # Tasks with deadlines first, sorted by date, then tasks without deadlines
    filtered_tasks = sorted(filtered_tasks, key=lambda t: (t['deadline'] is None,
                                                           t['deadline'] if t['deadline'] else datetime.max.date()))
elif sort_option == "Deadline (Latest First)":
    # Tasks with deadlines first (latest first), then tasks without deadlines
    filtered_tasks = sorted(filtered_tasks, key=lambda t: (t['deadline'] is None,
                                                           t['deadline'] if t['deadline'] else datetime.min.date()),
                            reverse=True)

if filtered_tasks:
    st.write(f"**{len(filtered_tasks)} task(s) found**")

    # Display tasks
    for task in filtered_tasks:
        # Check if this task is being edited
        is_editing = st.session_state.editing_task_id == task['id']

        if is_editing:
            # Edit mode
            with st.container():
                st.markdown("### ✏️ Editing Task")

                edit_desc = st.text_area(
                    "Description",
                    value=task['description'],
                    key=f"edit_desc_{task['id']}"
                )

                col1, col2 = st.columns(2)
                with col1:
                    edit_deadline = st.date_input(
                        "Deadline",
                        value=task['deadline'],
                        key=f"edit_deadline_{task['id']}"
                    )

                with col2:
                    if st.session_state.categories:
                        edit_categories = st.multiselect(
                            "Categories",
                            options=[c['id'] for c in st.session_state.categories],
                            default=task['categories'],
                            format_func=lambda x: get_category_by_id(x)['description'],
                            key=f"edit_categories_{task['id']}"
                        )
                    else:
                        edit_categories = []

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save", key=f"save_{task['id']}", type="primary"):
                        if edit_desc.strip():
                            edit_task(task['id'], edit_desc, edit_deadline, edit_categories)
                            st.session_state.editing_task_id = None
                            st.success("Task updated!")
                            st.rerun()
                        else:
                            st.warning("Description cannot be empty.")

                with col2:
                    if st.button("❌ Cancel", key=f"cancel_{task['id']}"):
                        st.session_state.editing_task_id = None
                        st.rerun()

                st.divider()
        else:
            # View mode
            with st.container():
                col1, col2, col3, col4 = st.columns([0.5, 5, 1, 1])

                with col1:
                    current_complete = task['complete']
                    new_complete = st.checkbox(
                        "✓",
                        value=current_complete,
                        key=f"complete_{task['id']}",
                        label_visibility="collapsed"
                    )
                    if new_complete != current_complete:
                        mark_task_complete(task['id'], new_complete)
                        st.rerun()

                with col2:
                    # Task description
                    if task['complete']:
                        st.markdown(f"~~{task['description']}~~")
                    else:
                        st.markdown(f"**{task['description']}**")

                    # Display categories
                    if task['categories']:
                        category_tags = []
                        for cat_id in task['categories']:
                            cat = get_category_by_id(cat_id)
                            if cat:
                                category_tags.append(
                                    f"<span style='background-color: {cat['color']}; color: white; "
                                    f"padding: 2px 8px; border-radius: 10px; font-size: 0.8em; margin-right: 5px;'>"
                                    f"{cat['description']}</span>"
                                )
                        st.markdown(" ".join(category_tags), unsafe_allow_html=True)

                    # Display deadline
                    if task['deadline']:
                        deadline_str = task['deadline'].strftime("%Y-%m-%d")
                        days_until = (task['deadline'] - datetime.now().date()).days

                        if days_until < 0:
                            st.markdown(f"🔴 Overdue: {deadline_str}")
                        elif days_until == 0:
                            st.markdown(f"🟡 Due today: {deadline_str}")
                        elif days_until <= 3:
                            st.markdown(f"🟠 Due soon: {deadline_str}")
                        else:
                            st.markdown(f"📅 Deadline: {deadline_str}")

                with col3:
                    if st.button("✏️ Edit", key=f"edit_{task['id']}"):
                        st.session_state.editing_task_id = task['id']
                        st.rerun()

                with col4:
                    if st.button("🗑️ Delete", key=f"delete_{task['id']}"):
                        delete_task(task['id'])
                        if st.session_state.editing_task_id == task['id']:
                            st.session_state.editing_task_id = None
                        st.rerun()

                st.divider()
else:
    st.info("No tasks found. Add your first task!")

# Footer with statistics
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    total_tasks = len(st.session_state.tasks)
    st.metric("Total Tasks", total_tasks)

with col2:
    completed_tasks = len([t for t in st.session_state.tasks if t['complete']])
    st.metric("Completed", completed_tasks)

with col3:
    pending_tasks = total_tasks - completed_tasks
    st.metric("Pending", pending_tasks)