from src.platform.scenes.arcade_shelf_scene import compute_arcade_shelf_layout, compute_shelf_cards


def test_arcade_layout_prioritizes_hero_and_shelf():
    import pygame

    layout = compute_arcade_shelf_layout(pygame, (1440, 900))

    assert layout.hero.width == layout.shelf.width
    assert layout.hero.height > layout.shelf.height
    assert layout.hero.bottom < layout.shelf.top
    assert layout.shelf.bottom < layout.footer.top


def test_arcade_layout_scales_to_laptop_size():
    import pygame

    layout = compute_arcade_shelf_layout(pygame, (960, 720))

    assert layout.hero.width > 800
    assert layout.hero.height >= 210
    assert layout.shelf.height >= 188


def test_shelf_centers_cards_when_they_fit():
    import pygame

    shelf = pygame.Rect(40, 500, 1200, 220)
    cards = compute_shelf_cards(pygame, shelf, 4, selected_index=0)

    assert len(cards) == 4
    assert cards[0].left >= shelf.left
    assert cards[-1].right <= shelf.right
    assert cards[0].top > shelf.top


def test_shelf_keeps_selected_card_fully_visible():
    import pygame

    shelf = pygame.Rect(20, 420, 640, 200)
    cards = compute_shelf_cards(pygame, shelf, 8, selected_index=6)

    assert cards[6].left >= shelf.left
    assert cards[6].right <= shelf.right
