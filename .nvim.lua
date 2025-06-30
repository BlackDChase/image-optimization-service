---@diagnostic disable: undefined-global

vim.opt.textwidth = 80
vim.opt.breakindent = true
vim.opt.linebreak = true

vim.api.nvim_create_user_command('DockerComposeReload', function()
    local target_winid = nil
    local target_bufnr = nil

    for _, winid in ipairs(vim.api.nvim_tabpage_list_wins(0)) do
        local bufnr = vim.api.nvim_win_get_buf(winid)
        if vim.api.nvim_buf_get_option(bufnr, 'buftype') == 'terminal' then
            target_winid = winid
            target_bufnr = bufnr
            break
        end
    end

    if not target_winid then
        vim.cmd('vsplit | terminal')
        target_bufnr = vim.api.nvim_get_current_buf()
        target_winid = vim.api.nvim_get_current_win()
    else
        vim.api.nvim_set_current_win(target_winid)
    end

    local job_id = vim.b[target_bufnr].terminal_job_id
    if job_id then
        vim.api.nvim_chan_send(job_id, 'docker compose down\n')
        vim.api.nvim_chan_send(job_id, 'docker compose up --build\n')

        vim.api.nvim_feedkeys('i' .. vim.api.nvim_replace_termcodes('<esc>', true, true, true), 'n', false)
    else
        vim.notify('Could not find terminal job ID for buffer ' .. target_bufnr, vim.log.ERROR)
    end
end, {
    desc = 'Reload Docker Compose (down then up --build)'
})

vim.keymap.set('n', '<leader>dd', ':DockerComposeReload<CR>', {
    desc = 'Reload Docker Compose (down then up --build)'
})
