#
# self.ohurt = [
#     Object(
#         -12000,
#         self.screen.get_height() + 40 + 100,
#         12000 * 2,
#         self.screen.get_height(),
#         (255, 75, 75),
#         self.screen,
#     )
# ]
# self.checkpoints = [
#     CheckpointObject(
#         1200,
#         0,
#         50,
#         self.screen.get_height(),
#         (175, 255, 175),
#         self.screen,
#         (1200, 1200),
#         "in the lava",
#     ),
#     CheckpointObject(
#         100,
#         0,
#         50,
#         self.screen.get_height(),
#         (175, 255, 175),
#         self.screen,
#         (100, 1200),
#         "spawn",
#     ),
# ]
#
# self.objects = [
#     Object(
#         300, self.screen.get_height() - 200, 50, 50, (255, 0, 255), self.screen
#     ),
#     Object(
#         600,
#         self.screen.get_height() - 200,
#         50,
#         250,
#         (175, 255, 175),
#         self.screen,
#     ),
#     # Object(
#     #     -600, self.screen.get_height(), 12000, 50, (100, 155, 255), self.screen
#     # ),
#     *[
#         Object(
#             -600 + 50 * i,
#             self.screen.get_height() + random.randint(-2, 2),
#             40,
#             40,
#             (55, 55, 55),
#             self.screen,
#         )
#         for i in range(1200)
#         if not i % 10 == 0 and not (i - 1) % 10 == 0
#     ],
# ]
